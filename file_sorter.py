import re  # For detecting the date of the pdf and job #
import pathlib
import shutil

# Use pathlib to define paths
destination = pathlib.Path("C:/DESTINATION/PATH/HERE")
source = pathlib.Path("C:/SOURCE/REPO/PATH/HERE") # aka where this directory is

def main():
    if len(list(source.iterdir())) > 0:
        test1 = findFileInfo()
        print(test1)
        getJobFolders(test1)
    else:
        print("There are no files to sort.")
    # moveFiles(test1)

def findFileInfo():
    filesanddates = {}  # job number : list of filenames
    for filename in source.iterdir():  # Extract job numbers attached to routing sheets
        res = re.findall(r"\d{6}-", filename.name)
        if res:
            if res[0][:-1] in filesanddates:
                filesanddates[res[0][:-1]].append(filename)
            else:
                filesanddates[res[0][:-1]] = [filename]
    return filesanddates

def getJobFolders(file_info):
    jobsfolder = list(destination.iterdir())
    # let's go through all of the files and find out where we need to shove it
    for folder in jobsfolder:
        filtered_num = folder.name[:6]  # job num is last six digits
        if filtered_num in file_info:
            for filename in file_info[filtered_num]:
                # Ending in actual directories is always one of the two options below
                routing_sheet_path = folder / "Routing Sheet"
                routing_sheets_path = folder / "Routing Sheets"
                if routing_sheet_path.is_dir():
                    ending = "Routing Sheet"
                else:
                    ending = "Routing Sheets"
                try:
                    shutil.move(str(filename), str(folder / ending / filename.name))
                except shutil.Error:
                    print(f"File \"{filename.name}\" already exists. Deleting file.")
                    filename.unlink() 
                else:
                    print(f"{filename.name} successfully moved into {folder.name}!")

if __name__ == "__main__":
    main()
