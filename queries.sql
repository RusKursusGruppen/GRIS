-- debtors and creditors
select * from (select creditor as user from entries where b_id = "1") union select debtor as user from debts left outer join entries using(e_id) where b_id = "1";

-- debtors, creditors and participants in a book
select * from (select creditor as user from entries where b_id = "1") union select debtor as user from debts left outer join entries using(e_id) where b_id = "1" union select participant as user from Book_participants where b_id = "1";





-- credits
select creditor as user, sum(amount) as credit from entries where b_id = "1" group by creditor;




--share_totals
select e_id, sum(share) as share_total from Debts group by e_id;

-- Entries with share_totals
select * from Entries left outer join (select e_id, sum(share) as share_total from Debts group by e_id) using (e_id) where b_id = "1";

-- debts with entry information
select * from debts left outer join entries using(e_id);

-- debts with entry + share_totals
select * from debts left outer join entries using(e_id) left outer join (select e_id, sum(share) as share_total from Debts group by e_id) using(e_id) where b_id = "1";

-- debts with entry + share_totals + owes
select *, ((amount*1.0)/share_total*share) as debt from debts left outer join entries using(e_id) left outer join (select e_id, sum(share) as share_total from Debts group by e_id) using(e_id) where b_id = "1";


-- total debt
select debtor as user, sum(debt) as debt from (select *, ((amount*1.0)/share_total*share) as debt from debts left outer join entries using(e_id) left outer join (select e_id, sum(share) as share_total from Debts group by e_id) using(e_id) where b_id = "1") group by debtor;




-- breakdown, no totals
select * from (select * from (select creditor as user from entries where b_id = "1") union select debtor as user from debts left outer join entries using(e_id) where b_id = "1" union select participant as user from Book_participants where b_id = "1")    left outer join    (select creditor as user, sum(amount) as credit from entries where b_id = "1" group by creditor) using (user)    left outer join    (select debtor as user, sum(debt) as debt from (select *, ((amount*1.0)/share_total*share) as debt from debts left outer join entries using(e_id) left outer join (select e_id, sum(share) as share_total from Debts group by e_id) using(e_id) where b_id = "1") group by debtor) using(user);

-- breakdown
select *, (ifnull(credit, 0)-ifnull(debt,0)) as total from (select * from (select creditor as user from entries where b_id = "1") union select debtor as user from debts left outer join entries using(e_id) where b_id = "1" union select participant as user from Book_participants where b_id = "1")    left outer join    (select creditor as user, sum(amount) as credit from entries where b_id = "1" group by creditor) using (user)    left outer join    (select debtor as user, sum(debt) as debt from (select *, ((amount*1.0)/share_total*share) as debt from debts left outer join entries using(e_id) left outer join (select e_id, sum(share) as share_total from Debts group by e_id) using(e_id) where b_id = "1") group by debtor) using(user);
