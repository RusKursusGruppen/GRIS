
Old style, manually creating variables and feeding it all to
data.execute. Notice how you have to specify every attribute 4 times

        username = session["username"]
        name = request.form["name"]
        address = request.form["address"]
        zipcode = request.form["zipcode"]
        city = request.form["city"]
        phone = request.form["phone"]
        email = request.form["email"]
        birthday = request.form["birthday"]
        driverslicence = 1 if "driverslicence" in request.form else 0
        diku_age = request.form["diku_age"]
        earlier_tours = request.form["earlier_tours"]
        about_me = request.form["about_me"]
        data.execute("UPDATE Users SET name=?,address=?,zipcode=?,city=?,phone=?,email=?,birthday=?,driverslicence=?,diku_age=?,earlier_tours=?, about_me=? WHERE username = ?", name, address,zipcode,city,phone,email,birthday,driverslicence,diku_age,earlier_tours,about_me,username)


First itteration of Buckets(still a fine way to do it)
        b = data.Bucket()
        b.name           = request.form["name"]
        b.address        = request.form["address"]
        b.zipcode        = request.form["zipcode"]
        b.city           = request.form["city"]
        b.phone          = request.form["phone"]
        b.email          = request.form["email"]
        b.birthday       = request.form["birthday"]
        b.driverslicence = 1 if "driverslicence" in request.form else 0
        b.diku_age       = request.form["diku_age"]
        b.earlier_tours  = request.form["earlier_tours"]
        b.about_me       = request.form["about_me"]

        data.store(s, "UPDATE Users $ WHERE username = ?", username)
alternative:
        b = data.Bucket(
            name           = request.form["name"],
            address        = request.form["address"],
            zipcode        = request.form["zipcode"],
            city           = request.form["city"],
            phone          = request.form["phone"],
            email          = request.form["email"],
            birthday       = request.form["birthday"],
            driverslicence = 1 if "driverslicence" in request.form else 0,
            diku_age       = request.form["diku_age"],
            earlier_tours  = request.form["earlier_tours"],
            about_me       = request.form["about_me"])

        data.store(s, "UPDATE Users $ WHERE username = ?", username)
Also instead of
        data.store(s, "UPDATE Users $ WHERE username = ?", username)
You could write
        b >> "(UPDATE Users $ WHERE username = ?", username)
As in "Pour the content of the bucket into this sql query at the '$'"


Buckets have further been extended so you can write the minimalistic:
        b = data.Bucket(request.form)
        b.name
        b.address
        b.zipcode
        b.city
        b.phone
        b.email
        b.birthday
        b.driverslicence
        b.diku_age
        b.earlier_tours
        b.about_me
        b >> ("UPDATE Users $ WHERE username = ?", username)

First a bucket is created with a dictionary. This dictionarry can contain
userspecified strings as its keys therefore making it unsafe to upload into the
database.  when you access an attribute the programmer has to use unquoted form,
which cannot be done with a string. Thereby the bucket knows that this attribute
is safe and that it is to be poured into the database.  So a bucket will only
pour content that has been verified by accessing it as either an attribute of
the bucketobject or by stating it as a keyword argument in its creation.
