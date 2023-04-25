import pdfplumber
from difflib import SequenceMatcher


# To check the plagiarism
def Check_Plagiarism(userfile,adminfile):
    with open(userfile) as file1, open(adminfile) as file2:
    
        file1data = file1.read()
        file2data = file2.read()

        #return the plagiarism percentage 
        return (SequenceMatcher(None, file1data, file2data).ratio())*100


# To Assign the marks Automatically
def autoMarkAssign(plagPercent):
    #Assigns the marks based on the plagpercent

    if plagPercent>90.00:
        return 10
    elif plagPercent > 80.00:
        return 9
    elif plagPercent > 75.00:
        return 8
    elif plagPercent  > 60.00:
        return 7
    elif plagPercent > 50.00:
        return 6
    else:
        return 5


#To convert PDF to TEXT using pdfplumber
def PdfToText(conversionFile):
    with pdfplumber.open(conversionFile) as pdf:
        text=''
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[0]
            text += page.extract_text(x_tolerance=2)
        return text
    


#Extract the data from the user file and write the data in user.txt 
def writeTextUser(userFile):
    open('user.txt', 'w').close()
    with open('user.txt', 'w') as txt_file:
        txt_file.write(PdfToText(userFile))

#Extract the data fromthe Faculty file and write the data in faculty.txt 
def writeTextFaculty(facultyFile):
    open('faculty.txt', 'w').close()
    with open('faculty.txt', 'w') as txt_file:
        txt_file.write(PdfToText(facultyFile))

def isFileAccepting():
    statusFlag=0
    if Check_Plagiarism('user.txt','faculty.txt') > 50:
        return 1
    return 0
    

#main function
def main():
    writeTextUser('test.pdf')
    writeTextFaculty('test2.pdf')
    plagCheck=Check_Plagiarism('user.txt','faculty.txt')
    print('Mark is: ',autoMarkAssign(plagCheck))


# main()