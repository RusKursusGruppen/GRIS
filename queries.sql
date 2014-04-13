-- debtors and creditors in a book
SELECT * FROM (SELECT creditor AS user FROM entries WHERE b_id = "1") UNION SELECT debtor AS user FROM debts LEFT OUTER JOIN entries USING(e_id) WHERE b_id = "1";

-- debtors, creditors and participants in a book
SELECT * FROM (SELECT creditor AS user FROM entries WHERE b_id = "1") UNION SELECT debtor AS user FROM debts LEFT OUTER JOIN entries USING(e_id) WHERE b_id = "1" UNION SELECT participant AS user FROM Book_participants WHERE b_id = "1";





-- creditors and credits in a book
SELECT creditor AS user, SUM(amount) AS credit FROM entries WHERE b_id = "1" GROUP BY creditor;




-- share_totals: total amount of shares per entry
SELECT e_id, SUM(share) AS share_total FROM Debts GROUP BY e_id;

-- Entries with share_totals per book
SELECT * FROM Entries LEFT OUTER JOIN (SELECT e_id, SUM(share) AS share_total FROM Debts GROUP BY e_id) USING (e_id) WHERE b_id = "1";


-- debts with entry information
SELECT * FROM debts LEFT OUTER JOIN entries USING(e_id);

-- debts with entry + share_totals
SELECT * FROM debts LEFT OUTER JOIN entries USING(e_id) LEFT OUTER JOIN (SELECT e_id, SUM(share) AS share_total FROM Debts GROUP BY e_id) USING(e_id) WHERE b_id = "1";

-- debts with entry + share_totals + owes
SELECT *, ((amount*1.0)/share_total*share) AS debt FROM debts LEFT OUTER JOIN entries USING(e_id) LEFT OUTER JOIN (SELECT e_id, SUM(share) AS share_total FROM Debts GROUP BY e_id) USING(e_id) WHERE b_id = "1";


-- total debt
SELECT debtor AS user, SUM(debt) AS debt FROM (SELECT *, ((amount*1.0)/share_total*share) AS debt FROM debts LEFT OUTER JOIN entries USING(e_id) LEFT OUTER JOIN (SELECT e_id, SUM(share) AS share_total FROM Debts GROUP BY e_id) USING(e_id) WHERE b_id = "1") GROUP BY debtor;

-- local total debt to you
select *, sum(debt) as debt from (SELECT *, ((amount*1.0)/share_total*share) AS debt FROM debts LEFT OUTER JOIN entries USING(e_id) LEFT OUTER JOIN (SELECT e_id, SUM(share) AS share_total FROM Debts GROUP BY e_id) USING(e_id) WHERE b_id = "1") where creditor == "rkg" group by debtor;



-- breakdown, no totals
SELECT * FROM (SELECT * FROM (SELECT creditor AS user FROM entries WHERE b_id = "1") UNION SELECT debtor AS user FROM debts LEFT OUTER JOIN entries USING(e_id) WHERE b_id = "1" UNION SELECT participant AS user FROM Book_participants WHERE b_id = "1")    LEFT OUTER JOIN    (SELECT creditor AS user, SUM(amount) AS credit FROM entries WHERE b_id = "1" GROUP BY creditor) USING (user)    LEFT OUTER JOIN    (SELECT debtor AS user, SUM(debt) AS debt FROM (SELECT *, ((amount*1.0)/share_total*share) AS debt FROM debts LEFT OUTER JOIN entries USING(e_id) LEFT OUTER JOIN (SELECT e_id, SUM(share) AS share_total FROM Debts GROUP BY e_id) USING(e_id) WHERE b_id = "1") GROUP BY debtor) USING(user);

-- breakdown returning float (* 1.0 instead of * 1)
SELECT *, (IFNULL(credit, 0)-IFNULL(debt,0)) AS balance FROM (SELECT * FROM (SELECT creditor AS user FROM entries WHERE b_id = "1") UNION SELECT debtor AS user FROM debts LEFT OUTER JOIN entries USING(e_id) WHERE b_id = "1" UNION SELECT participant AS user FROM Book_participants WHERE b_id = "1")    LEFT OUTER JOIN    (SELECT creditor AS user, SUM(amount) AS credit FROM entries WHERE b_id = "1" GROUP BY creditor) USING (user)    LEFT OUTER JOIN    (SELECT debtor AS user, SUM(debt) AS debt FROM (SELECT *, ((amount*1.0)/share_total*share) AS debt FROM debts LEFT OUTER JOIN entries USING(e_id) LEFT OUTER JOIN (SELECT e_id, SUM(share) AS share_total FROM Debts GROUP BY e_id) USING(e_id) WHERE b_id = "1") GROUP BY debtor) USING(user);





--- local_totals_sql = """
SELECT *
FROM
  (SELECT creditor,
          SUM(owes) AS total
   FROM

     /* raw_entries_sql: */
     (SELECT *,
      ((amount*1)/share_total*share) AS owes
      FROM
        (SELECT *
         FROM Entries
         WHERE b_id = "1")
      LEFT OUTER JOIN
        (SELECT e_id,
                SUM(share) AS share_total
         FROM Debts
         GROUP BY e_id)
        USING (e_id)
      LEFT OUTER JOIN
        (SELECT e_id,
                share
         FROM Debts
         WHERE debtor = "rkg")
        USING(e_id))

   GROUP BY creditor)
WHERE total is not Null AND creditor != "rkg"
--- """




select *, sum(debt) as debt from (SELECT *, ((amount*1.0)/share_total*share) AS debt FROM debts LEFT OUTER JOIN entries USING(e_id) LEFT OUTER JOIN (SELECT e_id, SUM(share) AS share_total FROM Debts GROUP BY e_id) USING(e_id) WHERE b_id = "1") where creditor == "rkg" group by debtor;

-- calculate who you owes money to -- local_totals
-- subtract
-- calculate who owes money to you
