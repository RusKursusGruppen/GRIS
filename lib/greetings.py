# -*- coding: utf-8 -*-

import random, subprocess
from lib import data

def random_greeting():
    result = random.choice(
        [ "GRIS"
        , "Bacon"
        , "Velkommen"
        , "Nu med ekstra procenter!"
        , "made in Emacs"
        , "GTs inside"
        , "Der er <i>n</i> dage til rusturen"
        , "git push -f"
        , lambda: "8"+("="*random.randint(1,17))+"D"
        , lambda: ("_-‾-"*random.randint(1,10))+"=:>"
        , ":(){ :|:& };:"
        , "public static void main(String[] args) {"
        , "Søren lavede denne side"
        , "Caro har også hjulpet"
        , "Formanden er dum!"
        , "Er du bange for tyngdekraften?"
        , "git@github.com:RusKursusGruppen/GRIS.git"
        , "Drevet af Flask, GT flask..."
        , "IT-Kalifen er en slacker!"
        , "Robert'); DROP TABLE Students;--"
        , "[]"
        , "<a href=\"http://en.wikipedia.org/wiki/Special:Random\">Learn more:</a>"
        , "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>."
        , lambda: "Der er {0} russer i databasen".format(data.execute("SELECT COALESCE(COUNT(r_id),0) FROM Russer")[0][0])
        , lambda: "<i>Latest commit message:</i> " + subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).decode('utf-8').rstrip('\n')
        , lambda: "<i>Latest committer:</i> " + subprocess.check_output(['git', 'log', '-1', '--pretty=%an']).decode('utf-8').rstrip('\n')
        , lambda: "<i>Latest commit date:</i> " + subprocess.check_output(['git', 'log', '-1', '--pretty=%ad']).decode('utf-8').rstrip('\n')
        , "Emacs, den objektivt bedste editor"
        , "O(n²)"
        , "λf.(λx.f (x x)) (λx.f (x x))"
        , "Kodet med knytnæver!"
        , "Søren har udviklet RKG-OS i skyen der kan ALT!"
        , "Søren snakker om kommunister og skinke!"
        , "Lund er nizzle i haven. NB og Munksgaard er nice og pooler"
        , "Nu gør RKG som vi plejer og kører en ligegyldig kommentar op til en laaaaang debat hvor alle skal sige det samme som de andre men blot med et lille twist (not)!"
        , "lalalalalala..."
        , "Vi har mange programmer til ølregnskab... alle er i BETA"
        , "rkg@dikumail.dk"
        , "qsort (p:xs) = qsort [x | x<-xs, x<p] ++ [p] ++ qsort [x | x<-xs, x>=p]"
        , "3% kode, 79% slam"])

    if callable(result):
        return result()
    return result
