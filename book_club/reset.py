'''
This script to reset migrations and delete database for this project.
NOTE: This file must placed into the django project folder
and run it by type "python reset.py"
'''
import os
import shutil
import glob
# Stopping paramter
check = True
delete_media = False
# loop for input corection
while check:
    # check whether user want to continue or not
    print('This will delete all migraions include your database.')
    con = input('Do you want to continue [y/n]:')
    # alaysis the answer
    if con == 'n':
        # quit
        print('Thank you or using reset script.')
        check = False
    elif con == 'y':
        # get the project path
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        # get a list of all files and folders the project contains
        content = os.listdir(BASE_DIR)
        # create a new list for folders only
        dirs = list()
        # filter the list of all content to get the folders only
        for dir in content:
            if os.path.isdir(os.path.join(BASE_DIR, dir)):
                dirs.append(dir)
        # clean up all folders
        for dir in dirs:
            # clean __pycache__ in all folders
            try:
                shutil.rmtree(f'{dir}/__pycache__')
                print(f'Folder __pycache__ in {dir} has been removed!')
            except Exception:
                pass
            # clean __pycache__ in all migrations folders
            try:
                shutil.rmtree(f'{dir}/migrations/__pycache__')
                print(f'Folder __pycache__ in \
                        {dir} /migations has been removed!')
            except Exception:
                pass
            # delete all migrations files except __init__.py
            try:
                FolderPath = os.path.join(BASE_DIR, dir, 'migrations')
                FolderContent = os.listdir(FolderPath)
                for file in FolderContent:
                    if not file == '__init__.py':
                        os.remove(os.path.join(FolderPath, file))
                        print(f'{FolderPath}{file} has been removed')
            except Exception:
                pass
            # delete .sqlite3 file
            try:
                for file in glob.glob("*.sqlite3"):
                    os.remove(file)
                    print(f'{file} has been removed')
            except Exception:
                pass
        while delete_media:
            # check whether user want to deleter media files or not
            mcon = input('Do you want to delete all media files? [y/n]:')
            # alaysis the answer
            if mcon == 'n':
                # quit
                print('Your media files still remains.')
                delete_media = False
            elif mcon == 'y':
                # get media folder
                mediapath = os.path.join(BASE_DIR, 'media')
                # get a list of all files and folders media contains
                media_content = os.listdir(mediapath)
                # create a new list for folders only
                media_dirs = list()
                # filter the list of all content to get the media folders only
                for dir in media_content:
                    if os.path.isdir(os.path.join(mediapath, dir)):
                        media_dirs.append(dir)
                # delete all files on the media root folder
                for file in media_content:
                    try:
                        os.remove(os.path.join(mediapath, file))
                        print(f'{mediapath}/{file} has been removed')
                    except Exception:
                        pass
                # clean up all folders
                for dir in media_dirs:
                    # get the folder path
                    FolderDir = os.listdir(os.path.join(mediapath, dir))
                    # delete all files on the media root subfolder
                    for file in FolderDir:
                        print(file)
                        try:
                            os.remove(os.path.join(mediapath, dir, file))
                            print(f'{mediapath}/{dir}/{file} has been removed')
                        except Exception:
                            pass
                print('All media files have been removed')
                delete_media = False
        print('\nYour project has been reset.\
                \nPlease migrate again before use.')
        check = False
    else:
        print("Invalid input. please input 'y' or 'n'.\n")
quit()