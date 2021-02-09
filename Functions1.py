import mysql.connector
import re

class queryManager():
    def __init__(self, User,LocalHost,Passwd):
        self.mydb = mysql.connector.connect(user=User, host=LocalHost, passwd=Passwd)
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("Use ogrod_zoologiczny")
        self.entities=self.initateTableList()
        self.basicQuery="select * from "
        self.currentQuery=""
        self.neighborhoodList=self.initateNeighborhoodList()
        print(self.neighborhoodList)

    def selectFilteredTable(self, name=""):
        table_name=""
        if name=="":
            table_name=self.chooseTable()
        else:
            table_name=name
        tablica=self.getColumns(table_name)# poczatkowa wartosc

        query = "select "
        query2=""

        current_table_name=table_name
        help_table=[table_name+"."+table_name+"_id"]
        if (not self.neighborhoodList.get(current_table_name) is None):
            help_table.append(table_name+"."+self.neighborhoodList.get(current_table_name)+"_id")
            help_table.append(self.neighborhoodList.get(current_table_name) + "." + self.neighborhoodList.get(current_table_name) + "_id")
            print(help_table)
            switcher=1
            switcher1=0
            #wybor atrybutow, domyslnie 1 join z wybranej przez nas tabeli, wybracnie kolejnego
            #klucza zewnetrznego powoduje rozszerzenie mozliwosci wyboru atrybutow
            while(switcher==1):
                if(switcher1==0):
                    tablica+=self.getColumns(self.neighborhoodList.get(current_table_name)) #rozszerzanie o zasieg join
                    query2 += self.generateJoin(current_table_name, self.neighborhoodList.get(current_table_name))
                    tablica = self.chooseColumns(tablica)  # choosing columns for select *** from#
                else:
                    print(current_table_name)
                    if (not self.neighborhoodList.get(current_table_name) is None):
                        second_table=self.getColumns(self.neighborhoodList.get(current_table_name))
                        query2 += self.generateJoin(current_table_name, self.neighborhoodList.get(current_table_name))
                        second_table = self.chooseColumns(second_table)  # choosing columns for select *** from#
                        tablica+=second_table
                    else:
                        break
                switcher=0
                for i in tablica:
                    print(i)
                    if ((type(re.search("\r*._id",i))is re.Match)) and  (not i in help_table):
                        switcher=1
                        switcher1=1
                        help_table.append(i)
                        help_table.append(((i.split(".")[1]).split("_"))[0]+"."+(i.split(".")[1]))
                        current_table_name=(i.split(".")[0])
                        print(help_table)
        else:
            tablica = self.chooseColumns(tablica)  # choosing columns for select *** from#

        #dodanie joinow do naszego zapytania, otrzymujemy klauzule select * from * join *
        index=0
        for i in tablica:
            query+=" "+i
            if(len(tablica)>1)and(index!=len(tablica)-1):
                query+=', '
            index+=1
        query += " from " + table_name
        if(query2!=""):
            query+=" "+query2

        #dodanie warunku
        if (len(tablica) > 0):
            condition_columns=""
            glue=["None"," or "," and "]
            answer=-1
            query2=""
            switcher=0
            while(1):
                condition_columns=self.choosePreciseColumn(tablica)
                condition = self.chooseCondtion()  # choosing the condition
                print('a')
                query2+=str(condition_columns)+str(condition)
                print("choose index 0-2: ")
                print(glue)
                answer=-1
                while(answer<0 or answer >len(glue)):
                    answer=int(input())
                if switcher==0:
                    query += " where " + query2
                    switcher=1
                else:
                    query+=" "+query2
                query2=""
                if answer==0:
                    break
                query2+=glue[answer]
        print(query)
        self.currentQuery=query
        return query

    def advancedFiltering(self):
        if(self.currentQuery==""):
            print("Error, you need to select data first")
            return
        answer=self.chooseFilteringObject("with what:  ")
        query=self.chooseAgregatedFunction()+"("+answer+"), "
        condition=" "
        while(condition==" "):
            condition=self.chooseCondtion()

        query2 = " group by " + self.chooseFilteringObject("for group of:  ") + " having "+ answer+ " "+condition
        self.currentQuery+=query2

        tablica=self.currentQuery.split(" ")
        for i in range(len(tablica)):
            if tablica[i]=="select":
                tablica[i]+=" "+query
                break
        query=" ".join(tablica)
        print(query)
        self.currentQuery=query
        return query

    #zmien dane pracownika
    def changeEmployeeData(self):
        table_name="pracownik"
        tablica = self.getColumns(table_name)  # poczatkowa wartosc
        for i in range(len(tablica)):
            print(str(i)+". "+tablica[i])
        answer=-1
        while(not(answer>=0 and answer<len(tablica))):
            answer=int(input("index of value to change: "))
        value = str(input("new value: "))
        answer1 = int(input("0 if string, else number: "))
        if(answer==0):
            value+='\''+value+'\''

        query="update "+table_name+" set "+tablica[answer]+"="+value+" where "

        condition_columns = ""
        glue = ["None", " or ", " and "]
        query2 = ""
        switcher = 0
        while (1):
            print("choose value you use as a filter: ")
            condition_columns = self.choosePreciseColumn(tablica)
            print("choose condtion: ")
            condition = self.chooseCondtion()  # choosing the condition
            query2 += str(condition_columns) + str(condition)
            print("choose index 0-2: ")
            print(glue)
            answer = -1
            while (answer < 0 or answer > len(glue)):
                answer = int(input())
            query+=query2
            if(answer==0):
                break
            else:
                query2=""
                query+=" "+glue[answer]
        print(query)
        self.mycursor.execute(query)
        return query

    def insertNewData(self):
        table_name = self.chooseTable()
        tablica = self.getColumns(table_name)  # poczatkowa wartosc
        tablica1=["null"]

        i=1
        while i<len(tablica)-1:
            print (tablica[i])
            a=int(input("0- string, else int: "))
            if a==0:
                tablica1.append(str(input(": ")))
            else:
                tablica1.append(int(input(": ")))
            i+=1
        if (table_name=="stanowisko"):
            tablica1.append(str(input("nazwa: ")))

        query="insert into "+table_name+" ("+ str(tablica[0])
        i=1
        while i<len(tablica):
            query+=", "+str(tablica[i])
            i+=1
        query+=") "

        if (table_name == "stanowisko"):
            query+="values ("+tablica1[0]+", \""+tablica1[1]+"\" )"
            print(query)
            return query

        answer = int(input("0- i put connection manually, else- guide me: "))
        if (answer != 0):
            query+="select "
            query+=self.composeValuesForInsert(table_name,tablica1)
            query+=", "+str(tablica[len(tablica)-1].split(".")[1])
            query2=""
            answer=input("Use previously searched -0, else- new search ")
            if answer==0:
                query2=self.currentQuery
            else:
                query2=self.selectFilteredTable((((tablica[len(tablica)-1].split("."))[1]).split("_"))[0])
            query+=" from "+query2.split("from")[1]
            print(query)

        else:
            tablica1.append(int(input(": ")))
            query+="values ("
            query+=self.composeValuesForInsert(table_name,tablica1)
            query+=")"
            print(query)
        return query

    #Below is a section with helper funtions

    def composeValuesForInsert(self, table_name, table):
        self.mycursor.execute("show fields from "+str(table_name))
        lista=self.mycursor.fetchall()
        query=""
        if type(re.search("\r*.varchar\r*",str(lista[0]))) is None:
            query+=str(table[0])+" "
        else:
            query+="\""+str(table[0])+"\""
        i = 1
        while i < len(table):
            query += ", "
            if not type(re.search("\r*.varchar\r*", str(lista[i]))) is re.Match and type(re.search("\r*.enum\r*", str(lista[i]))) is re.Match:
                query += str(table[i]) + " "
            else:
                query += "\"" + str(table[i]) + "\""
            i += 1
        return query

    def chooseFilteringObject(self, tekst):
        possibleValues = self.extractAttributesFromString(self.currentQuery)
        answer = -1
        index = 0
        for i in range(len(possibleValues)):
            print(str(i) + ". " + possibleValues[i])
        while not (answer >= 0) and (answer < len(possibleValues)):
            answer = int(input(tekst))

        return possibleValues[answer]

    def chooseAgregatedFunction(self):
        functions = ["sum", "count", "avg"]
        index = 0
        for i in functions:
            print(str(index) + ". " + i)
            index += 1
        answer = -1
        while not (answer >= 0) and (answer < len(functions)):
            answer = int(input("what do you want to do: "))
        return functions[answer]

    def initateTableList(self):
        self.mycursor.execute("show tables")
        lista = self.mycursor.fetchall()
        properValues=[]
        for i in lista:
            a=((str(i)).split('\''))[1]
            properValues.append(a)
        return properValues

    def initateNeighborhoodList(self):
        connectios={}
        for i in self.entities:
            self.mycursor.execute("show columns from "+i)
            columns=self.mycursor.fetchall()

            for a in columns:
                if(type(re.search("\r*._id",str(a[0])))is re.Match):
                    if(((str(a[0])).split("_"))[0]!=i):
                        temp={i:((str(a[0])).split("_"))[0]}
                        connectios.update(temp)
        return connectios

    def chooseTable(self):
        index=0
        for i in self.entities:
            print(str(index)+ ". "+i)
            index+=1
        choice=-1
        while(not((choice>=0)and (choice<len(self.entities)))):
            choice=int(input("Numer tabeli: "))
        return self.entities[choice]

    def getColumns(self, table_name): #get all columns contained in particular table
        self.mycursor.execute("show columns  from "+str(table_name))
        i=self.mycursor.fetchall()
        columns=[]
        for a in i:
            columns.append(table_name+"."+a[0])
        return columns

    def chooseColumns(self, tablica): #from table of attributes, create new which contains only interesing elements
        if (len(tablica)==0) or (len(tablica)==1):
            return
        index=0
        for i in tablica:
            print (str(index)+". "+i)
            index+=1
        table=[]
        answer=-2
        while (not(answer==-1)):
            answer=int(input("index filtra, lub -1 by wyjsc"))
            if((answer>=0)and (len(tablica)>answer)):
                table.append(tablica[answer])
        return table

    def choosePreciseColumn(self, table): #choose precise column from table
        index=0
        for i in table:
            print(str(index)+". "+i)
            index+=1
        answer=-1
        while(not((answer>=0)and (answer<len(table)))):
            answer=int(input())
        return table[answer]

    def chooseCondtion(self):
        conditions=[' ','=','<=','>=',"<",">"," LIKE "," is "]
        index=0
        for i in conditions:
            print(str(index)+" ."+i)
            index+=1
        answer=-1
        while (not ((answer >= 0) and (answer < len(conditions)))):
            answer = int(input())
        value=""
        if not(answer==0):
            value=input("conditional value: ")
            if answer==6:
                value='\''+value+'\''
        return str(conditions[answer]+str(value))

    def generateJoin(self, table1, table2):
        print(table1)
        print(table2)
        query=" join "+ table2+" on "+ table1+"."+table2+"_id ="+table2+"."+table2+"_id"
        print(query)
        return query

    def extractAttributesFromString(self, tekst):
        tablica = tekst.split(" ")
        tablica2 = []
        for i in range(len(tablica)):
            if ((tablica[i] != "select") and (re.search("[a-zA-Z1-9_.]", tekst) is not None) and not tablica[i] == ""):
                if (tablica[i] == "from"):
                    break
                tablica2.append(tablica[i].split(",")[0])
        return tablica2

    #Below are simply made sql queries (simply- no code generator but canned transactions

    def changeEmployeeJob(self):
        self.mycursor.execute("select stanowisko_nazwa from stanowisko")
        lista=self.mycursor.fetchall()
        i=0
        while i<len(lista):
            print(i+". "+str(lista[i]))
            i+=1
        query = "update pracownik set pracownik.stanowisko_id="+str(lista[int(input("index: "))])
        return query

    def changeSectionManager(self):
        self.mycursor.execute("select sekcja_nazwa from sekcja")
        lista2 = self.mycursor.fetchall()
        i = 0
        while i < len(lista2):
            print(str(i) + ". " + str(lista2[i]))
            i += 1
        answer2 = input("Choose section: ")
        self.mycursor.execute("select nazwisko, imie from pracownik")
        lista = self.mycursor.fetchall()
        i = 0
        while i < len(lista):
            print(str(i) + ". " + str(lista[i]))
            i += 1
        answer=input("Choose new head of section: ")
        query="update sekcja set sekcja.pracownik_id=(select pracownik_id from pracownik where pracownik.nazwisko like "
        query+=(str((str(lista[int(answer)])).split(",")[0])).split("(")[1]
        query+=" and pracownik.imie like "
        query+=(str(str(lista[int(answer)]).split(",")[1])).split(")")[0]
        query+=") where sekcja_nazwa like "
        query+=str(str(lista2[int(answer2)]).split(",")[0]).split("(")[1]
        query+=""
        print(query)
        return query

    def changeBelongingOfSpecieToRun(self):
        self.mycursor.execute("select gatunek_nazwa from gatunek")
        lista2 = self.mycursor.fetchall()
        i = 0
        while i < len(lista2):
            print(str(i) + ". " + str(lista2[i]))
            i += 1
        answer2 = input("Choose specie: ")
        self.mycursor.execute("select wybieg_nazwa from wybieg")
        lista = self.mycursor.fetchall()
        i = 0
        while i < len(lista):
            print(str(i) + ". " + str(lista[i]))
            i += 1
        answer = input("Choose new run: ")
        query = "update sekcja set gatunek.wybieg_id=(select wybieg_id from wybieg where wybieg.nazwa like "
        query += str(str(lista[int(answer)]).split(",")[0]).split("(")[1]
        query += ") where sekcja_nazwa like "
        query += str(str(lista2[int(answer2)]).split(",")[0]).split("(")[1]
        print(query)
        return query

    def DeleteAnAnimal(self):
        self.mycursor.execute("select gatunek_nazwa from gatunek")
        lista2 = self.mycursor.fetchall()
        i = 0
        while i < len(lista2):
            print(str(i) + ". " + str(lista2[i]))
            i += 1
        answer2 = input("Choose specie: ")
        name=str(input("name: "))
        query="delete from zwierze where zwierze.gatunek_id =(select gatunek_id from gatunek where gatunek_nazwa like "
        query+=str((str(lista2[answer2])).split(",")[0]).split("(")[1]+" )"
        query+=" and zwierze_nazwa like "+name
        print(query)
        return query

    def DeleteEmployee(self): #none of sekcja can point to this employee
        name=str(input("Name: "))
        surname=str(input("Surname: "))
        query="delete from pracownik where imie=\""+name+"\" and nazwisko=\""+surname+" and pracownik_id not in (select sekcja.pracownik_id from sekcja)"
        print (query)
        return query


    def DeleteRun(self): #none of gatunek can point to this Run
        name = str(input("Run name: "))
        query = "delete from pracownik where wybieg_nazwa=\"" + name + "\" and wybieg_id not in (select wybieg_id from gatunek)"
        print(query)
        return query

    #this function execute query- let'say it would be view in mvc model if we would like to manage project further

    def runQuery(self, query):
        self.mycursor.execute(query)
        lista=self.mycursor.fetchall()
        for i in lista:
            print(i)
        answer=input("Press button...")


