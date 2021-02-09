import re



tekst="""wlazl kotel i mruga drugi wyraz ze zl na koncu krazl
      zobaczymy ile zl i wyrazow z zl na koncu jak azl wyszuka"""

'''
regex=re.search("\r*.zl",tekst)
print(type(regex))
'''
tekst="select  jedna.imie,  druga.nazwisko,  druga.trzecia_id,  trzecia.drugie_imie from jedna  join druga on jedna.druga_id =druga.druga_id join trzecia on druga.trzecia_id =trzecia.trzecia_id"
tablica=tekst.split(" ")
tablica2=[]

for i in range(len(tablica)):
    if((tablica[i]!="select")and (re.search("[a-zA-Z1-9_.]", tekst) is not None)and not tablica[i]==""):
        if(tablica[i]=="from"):
            break
        tablica2.append(tablica[i].split(",")[0])

print(tablica2)
for i in tablica2:
    print(i)
print(len(tablica2))





