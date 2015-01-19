# -*- coding: utf-8 -*-

import sys, itertools
import psycopg2, psycopg2.extras
from flask import _app_ctx_stack

from lib import log

class BucketDatabase():
    def __init__(self, app=None, context_stack=None):
        self.app = None
        self._stack = context_stack

        if app is not None:
            self.init_app(app, context_stack)

    def init_app(self, app, context_stack=None):
        # self._stack
        self._stack = context_stack #or self._stack
        if self._stack is None:
            self._stack = _app_ctx_stack

        self.app = app
        self.app.config.setdefault("BUCKET_DATABASE_HOST", "")
        self.app.config.setdefault("BUCKET_DATABASE_NAME", "")
        self.app.config.setdefault("BUCKET_DATABASE_USER", "")
        self.app.config.setdefault("BUCKET_DATABASE_PORT", "")
        self.app.config.setdefault("BUCKET_DATABASE_PASSWORD", "")
        self.app.teardown_appcontext(self.teardown)

    def teardown(self, exception):
        ctx = self._stack.top
        if hasattr(ctx, "bucket_transaction_stack"):
            ctx.bucket_transaction_stack.clear()

    def Bucket(self, *args, **kwargs):
        return Bucket(*args, **kwargs)

    def bucket_and_master(self, *args, **kwargs):
        bucket = Bucket(*args, **kwargs)
        master = BucketMaster(bucket)
        return bucket, master

    def transaction(self):
        ctx = self._stack.top
        if ctx is None or not hasattr(ctx, "bucket_transaction_stack") or len(ctx.bucket_transaction_stack) == 0:
            return self.new_transaction()
        return ctx.bucket_transaction_stack[-1]

    def new_transaction(self):
        return Transaction(self)

    def execute(self, query, *args):
        with self.transaction() as t:
            return t.execute(query, *args)

    def executemany(self, query, argSeq):
        with self.transaction() as t:
            return t.executemany(query, *args)

    def script(self, filename):
        with self.transaction() as t:
            return t.script(query, *args)

    def _push_transaction(self, transaction):
        ctx = self._stack.top
        if ctx is not None:
            if not hasattr(ctx, "bucket_transaction_stack"):
                ctx.bucket_transaction_stack = []
            ctx.bucket_transaction_stack.append(transaction)

    def _pop_transaction(self):
        ctx = self._stack.top
        if ctx is None or not hasattr(ctx, "bucket_transaction_stack"):
            raise Exception("Cant pop from empty stack")
        return ctx.bucket_transaction_stack.pop()


class Transaction():
    def __init__(self, bucketDatabase):
        self._bucketDatabase = bucketDatabase
        self._contextdepth = 0

        self.connection = psycopg2.connect(host=self._bucketDatabase.app.config["BUCKET_DATABASE_HOST"],
                                           database=self._bucketDatabase.app.config["BUCKET_DATABASE_NAME"],
                                           user=self._bucketDatabase.app.config["BUCKET_DATABASE_USER"],
                                           port=self._bucketDatabase.app.config["BUCKET_DATABASE_PORT"],
                                           password=self._bucketDatabase.app.config["BUCKET_DATABASE_PASSWORD"],
                                           cursor_factory=BucketCursor)

    def _execute(self, query, args, many):
        if query.count("?") != len(args):
            raise Exception("Wrong number of SQL arguments for query "+query)
        query = query.replace("?", "%s")
        try:
            # with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            with self.connection.cursor() as cursor:
                if many:
                    cursor.executemany(query, args)
                else:
                    cursor.execute(query, args)

                log.data(query, args)
                try:
                    return QueryList(cursor.fetchall())
                except psycopg2.ProgrammingError as e:
                    if str(e) == "no results to fetch":
                        return None
                    raise
        except:
            log.data(query, args, error=True)
            raise

    def execute(self, query, *args):
        return self._execute(query, args, False)

    def executemany(self, query, argSeq):
        args = []
        query_count = query.count("?")
        for arg in argSeq:
            # if argSeq is like ["a", "b", "c", "d", ...]
            if isinstance(arg, str):
                length = 1
                args.append((arg,))
            else:
                # if argSeq is like [("a", "b"), ("c", "d"), ...]
                try:
                    length = len(arg)
                    args.append(arg)
                # if argSeq is like [1, 2, 3, 4...] where the arguments are not strings
                except:
                    length = 1
                    args.append((arg,))
            if query_count != length:
                raise Exception("Wrong number of SQL arguments for query "+query)

        query = query.replace("?", "%s")
        return self._execute(query, args, True)

    def script(self, filename):
        with open(filename) as f:
            return self._execute(f.read())

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def __enter__(self):
        self._bucketDatabase._push_transaction(self)
        self._contextdepth += 1
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._bucketDatabase._pop_transaction()
        self._contextdepth -= 1
        if self._contextdepth == 0:
            self.commit()


class QueryList(list):
    def all(self):
        return self

    def one_or_more(self):
        if len(self) == 1:
            return self[0]
        else:
            return self

    def one(self, code=None, description=None):
        if len(self) != 1:
            if code is None and description is None:
                description = "There are {} rows in the result, but only one was expected!".format(len(self))
            abort(code, description)
        else:
            return self[0]

    def scalar(self, code=None, description=None):
        row = self.one(code, description)
        if len(row) != 1:
            if code is None and description is None:
                description = "There are {} columns in the result, but only one was expected!".format(len(self))
            abort(code, description)
        return row[0]

    def scalars(self, code=None, description=None):
        result = []
        for row in self:
            if len(row) != 1:
                if code is None and description is None:
                    description = "There are {} columns in the result, but only one was expected!".format(len(self))
                abort(code, description)
            result.append(row[0])
        return result

    def by_key(self, key):
        return {row[key]:row for row in self}

    def __html__(self):
        return dict(length=len(self),
                    values=[item.__html__() for item in self])


class Bucket():
    def __init__(self, *unsafe,  **kwargs):
        self._lock = False

        self._unsafe = {}
        for d in unsafe:
            # EXPLANATION:
            # You cant use self._unsafe.update(d) here as the request.form
            # for some reason will pack its values in lists
            for k,v in d.items():
                self._unsafe[k] = v

        for k,v in kwargs.items():
            object.__setattr__(self, k, v)

    def __getattribute__(self, item):
        """If there is an attribute 'item' in self, return it.
        If there is a key 'item' in __kv__ return the corresponding value, and insert it into the attributes.
        Else try to look up 'item' in self anyway probably triggering an exception"""

        if item in object.__getattribute__(self, "__dict__"):
            return object.__getattribute__(self, item)

        if not object.__getattribute__(self, "_lock"):
            unsafe = object.__getattribute__(self, "_unsafe")
            if item in unsafe:
                value = unsafe[item]
                object.__setattr__(self, item, value)
                return value

        return object.__getattribute__(self, item)

    def __call__(self):
        return BucketMaster(self)

    def __len__(self):
        keys = set(self)
        keys.update(self._unsafe.keys())
        return len(keys)

    def __contains__(self, item):
        try:
            self[item]
            return True
        except NameError:
            return False

    def __getitem__(self, item):
        """Returns item in the bucket or if none is found, the item in the unsafe part"""
        prevlock = self._lock
        + self
        try:
            return self.__getattribute__(item)
        except AttributeError:
            return self._unsafe[item]
        finally:
            self._lock = prevlock

    def __setitem__(self, item, value):
        prevlock = self._lock
        + self
        try:
            # WARNING: hasattr tries to access self.item so the bucket needs to be locked!!
            if hasattr(self, item):
                self.__setattr__(item, value)
            else:
                # Should not be reached unless python changes implementation of hasattr
                self._unsafe[item] = value
        except AttributeError:
            self._unsafe[item] = value
        finally:
            self._lock = prevlock

    def __pos__(self):
        self._lock = True

    def __neg__(self):
        self._lock = False

    def __html__(self):
        return self().all_dict()

    def __iter__(self):
        return ((k, self[k]) for k in dir(self) if not k.startswith("_"))

    def __repr__(self):
        keys = set(k for k,_ in self)
        result = "Bucket("
        result += ", ".join(k + " = " + repr(v) for k,v in self)
        result += " | unsafe: {"
        # result += repr(self._unsafe)
        result += ", ".join((k if isinstance(k, str) else repr(k)) + ": " + repr(v) for k,v in self._unsafe.items() if k not in keys)
        result += "})"
        return result

    def __rshift__(self, args):
        """Pour, into database"""
        sql = args[0]
        args = args[1:]

        setstatm = ", ".join(["{0} = ?".format(c) for c in self])
        if sql.lower().find(" set ") == -1:
            sql = sql.replace("$", "SET $")
        sql = sql.replace("$", setstatm)

        values = [self[c] for c in self]
        values.extend(args)

        return execute(sql, *values)

    def __ge__(self, dest):
        """Insert entry into database"""
        sql = "INSERT INTO {0}(".format(dest)
        keys = [c for c in self]
        questions = ["?"] * len(keys)
        values = [self[c] for c in self]

        sql += ",".join(keys)
        sql += ") VALUES ("
        sql += ",".join(questions)
        sql += ")"
        sql += " returning *"

        result = execute(sql, *values)
        return result.one_or_more()

class BucketMaster():
    def __init__(self, bucket):
        self._bucket = bucket

    def insert(self, destination):
        return self._bucket >= destination

    def pour(self, *args, **kwargs):
        return self.store(*args, **kwargs)

    def store(self, sql, *args):
        return self._bucket >> [sql]+list(args)


    def safe_keys(self):
        return (k for k,_ in self._bucket)

    def unsafe_keys(self):
        safe = set(self.safe_keys())
        return (k for k in self._bucket._unsafe if k not in safe)

    def all_keys(self):
        # Not all safe items are guaranteed to be in the unsafe ones
        return itertools.chain(self.safe_keys(), self.unsafe_keys())


    def safe_items(self):
        return iter(self._bucket)

    def unsafe_items(self):
        safe = set(self.safe_keys())
        return ((k, v) for k,v in self._bucket._unsafe.items() if k not in safe)

    def all_items(self, bucket):
        return itertools.chain(self.safe_items(), self.unsafe_items())


    def safe_dict(self):
        return {k:v for k,v in self.safe_items()}

    def unsafe_dict(self):
        return {k:v for k,v in self.unsafe_items()}

    def all_dict(self):
        return {k:v for k,v in self.all_items()}


class BucketCursor(psycopg2.extensions.cursor):
    def __init__(self, *args, **kwargs):
        super(BucketCursor, self).__init__(*args, **kwargs)
        self.row_factory = BucketRow
        self._column_mapping = None

    def column_mapping(self):
        if self._column_mapping is None:
            self._column_mapping = []
            for i in range(len(self.description)):
                self._column_mapping.append(self.description[i][0])
        return self._column_mapping


class BucketRow(Bucket):
    def __init__(self, cursor):
        super(BucketRow, self).__init__()
        self._column_mapping = cursor.column_mapping()

    def __getitem__(self, item):
        if isinstance(item, int):
            item = self._column_mapping[item]
        return super(BucketRow, self).__getitem__(item)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            key = self._column_mapping[key]
        return super(BucketRow, self).__setitem__(key, value)


def config_db(config = None):
    class DummyApp():
        def __init__(self, config):
            self.config = config
        def teardown_appcontext(self, *args, **kwargs):
            pass

    class DummyStack():
        top = Bucket()

    if config is None:
        import config
        app_config = {"BUCKET_DATABASE_HOST": config.BUCKET_DATABASE_HOST,
                      "BUCKET_DATABASE_NAME": config.BUCKET_DATABASE_NAME,
                      "BUCKET_DATABASE_USER": config.BUCKET_DATABASE_USER,
                      "BUCKET_DATABASE_PORT": config.BUCKET_DATABASE_PORT,
                      "BUCKET_DATABASE_PASSWORD": config.BUCKET_DATABASE_PASSWORD}
        app = DummyApp(app_config, _app_ctx_stack)
    else:
        app = DummyApp(config)
    return BucketDatabase(app, _app_ctx_stack)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python data.py SCRIPT")
    else:
        print(script(sys.argv[1]))
