import Functions1


class Interface:
    def __init__(self, user, host, passwd):
        self.functions=["Searching","Filtering","Change_employee_data",
                   "Change_section_keeper","Insert_data","Change_employee_position",
                  "Delete_animal","Delete_employee","Delete_run","Change_run_for_the_specie",
                    "Last_select","Exit"]
        self.QMan=Functions1.queryManager(user,host,passwd)


    def main(self):
        a=1
        while(a>=0):
            a=self.showMenuAndTakeAction()


    def showMenuAndTakeAction(self):
        for i in range(len(self.functions)):
            print(str(i)+". "+self.functions[i])
        answer=-1
        while not((answer>=0)and answer<len(self.functions)):
            answer=int(input("Your choice: "))
        return getattr(self,self.functions[answer])()

    def Searching(self):
        self.QMan.runQuery(self.QMan.selectFilteredTable())
        return 0

    def Filtering(self):
        self.QMan.runQuery(self.QMan.advancedFiltering())
        return 0

    def Change_employee_data(self):
        self.QMan.runQuery(self.QMan.changeEmployeeData())
        return 0

    def Change_section_keeper(self):
        self.QMan.runQuery(self.QMan.changeSectionManager())
        return 0

    def Insert_data(self):
        self.QMan.runQuery(self.QMan.insertNewData())
        return 0

    def Change_employee_position(self):
        self.QMan.runQuery(self.QMan.changeEmployeeJob())
        return 0

    def Delete_animal(self):
        self.QMan.runQuery(self.QMan.DeleteAnAnimal())
        return 0

    def Delete_employee(self):
        self.QMan.runQuery(self.QMan.DeleteEmployee())
        return 0

    def Delete_run(self):
        self.QMan.runQuery(self.QMan.DeleteRun())
        return 0

    def Change_run_for_the_specie(self):
        self.QMan.runQuery(self.QMan.changeBelongingOfSpecieToRun())
        return 0

    def Last_select(self):
        if not self.QMan.currentQuery=="":
            self.QMan.runQuery(self.QMan.currentQuery)
        else:
            print("There is no last selection")
        return 0

    def Exit(self):
        return -1


#print i #fullfill data Interface() and delete this line
a=Interface("root","localhost","Michal1$")
a.main()
