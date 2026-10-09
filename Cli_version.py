from pathlib import Path
print ("press 1 to create a file")
print("press 2 to read  a file")
print("press 3 to edit a file(includes rename,add content,delete the file)")

choose= int(input("enter your choice"))
def createfile():
    name= input("enter the name of file you want to crate")
    path= Path(name)
    if path.exists():
        print("file already exists")
    else:
        with open(path, "w") as f:
            content= input("want to write something ?")
            f.write(content)
            print("content has been added")
def readfile():
    name= input("enter the name of the file you want to read")
    path= Path(name)
    if path.exists():
        with open (path,"r") as f:
            content = f.read()
            print(content)
            
    else:
        print("file with that name doesn't exist")
def editfile():
    print("you want to write something? press1")
    print("you want to delete the file? press 2")
    print("you want to rename the file? press 3")
    choice=int(input("enter your choice"))
    if choice==1:
        name= input("enter the name of the file")
        path = Path(name)
        if path.exists():
            path.unlink()
            print("file has been deleted")
        else:
            print("file with that name doesn't exists")
    elif choice==2:
        with open (path,"a") as f:
            content = input("write what you want to add in the file")
            f.write(content) 
            print("file has been appended")
    elif choice==3:
        name= input("enter the name of the file")
        path = Path(name)
        if path.exists():
            name2= input("what's the newname you want to give to file")
            pathn= Path(name2)

            if pathn.exists():
                print("file with that name already exists")
            else:
                name.rename(f"{name2}.txt")
                print("file has been renamed")
if choose==1:
    createfile()
 
elif choose==2:
    readfile()
     
elif choose==3:
    editfile()
else:
    print("you entered non existent choice please read again and choose from the above given options only")