import mysql.connector
import re
#Plik z funkcjami wykonujacymi transakcje zapuszkowane
#narazie w formie protptypu, jesli starczy czasu, czesc z nich, badz wyszystkie
#zostana prekute w generator zapytan SQL

#standardem jest zwracanie wynikow

#1. Listowanie wszystkich encji


#function 1: list all the entities
#funciton 2: list and filter all the entities
class queryManager():
    def __init__(self):
        self.mydb = mysql.connector.connect(user="root", host="localhost", passwd="Michal1$")
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("Use voldemort")
        self.entities=self.initateTableList()
        self.basicQuery="select * from "
        self.currentQuery="select* from"
        self.neighborhoodList=self.initateNeighborhoodList()
        print(self.neighborhoodList)

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
        print("fun: "+str(table_name))
        print(type(table_name))
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

    def selectFilteredTable(self): #generate select* from * where * - bounds: there can be 1 where statement
        table_name=self.chooseTable()
        tablica=self.getColumns(table_name)# poczatkowa wartosc

        query = "select "
        query2=""

        current_table_name=table_name
        print(current_table_name)
        help_table=[table_name+"."+table_name+"_id"]
        if (not self.neighborhoodList.get(current_table_name) is None):
            help_table.append(table_name+"."+self.neighborhoodList.get(current_table_name)+"_id")
            help_table.append(self.neighborhoodList.get(current_table_name) + "." + self.neighborhoodList.get(current_table_name) + "_id")
            print(help_table)
            switcher=1
            switcher1=0
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

        #query += " from " + table_name

        #dodanie booleana, jesli true, konczymy rozszerzanie joinem, jesli nie, rozszerzamy o kolejny w iteracji

        index=0
        for i in tablica:
            query+=" "+i
            if(len(tablica)>1)and(index!=len(tablica)-1):
                query+=', '
            index+=1
        query += " from " + table_name
        if(query2!=""):
            query+=" "+query2
        #query+= self.generateJoin(table_name,self.neighborhoodList.get(table_name))


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
                #query+=" where "+query2#str(condition_columns)+str(condition)


        print(query)
        self.currentQuery=query
        self.mycursor.execute(query)
        return self.mycursor.fetchall()






obj=queryManager()


lista=obj.selectFilteredTable()
for i in lista:
    print(i)



'''
i=obj.selectEntities()
for a in i:
    print(a)

'''
