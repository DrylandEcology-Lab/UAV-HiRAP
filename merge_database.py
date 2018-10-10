import sqlite3
import platform

def replace_email_to_dtc(in_str, platform='Linux'):
    linux_str = ''
    for dir in in_str.split('/'):
        if '@' in dir:
            linux_str += 'dtc/'
        else:
            linux_str += dir + '/'
    if platform == 'Windows':
        out_str = linux_str.replace('/LocalDisk/Documents/UAV_HiRAP/',
                                    r'D:\OneDrive\Program\Python\MyProjects\UAV-HiRAP/')
    else:
        out_str = linux_str

    return out_str

if __name__ == '__main__':
    sys_str = platform.system()
    table_names = ['users','dtc_projects']

    db1 = sqlite3.connect("data-dev.sqlite")
    db2 = sqlite3.connect("data.sqlite")

    # replace user table
    fc = db1.execute('SELECT * FROM users').fetchall()
    length = len(fc[0])
    sql_user = 'INSERT INTO users VALUES (' + '?,' * (length - 1) + '?)'
    db2.executemany(sql_user, fc)

    # replace dtc_projects table
    fc = db1.execute('SELECT * FROM dtc_projects').fetchall()
    length = len(fc[0])
    sql_user = 'INSERT INTO dtc_projects VALUES (' + '?,' * (length - 1) + '?)'

    for var in fc:
        dir_1 = var[4]  #['', 'LocalDisk', 'Documents', 'UAV_HiRAP', 'app', 'static', 'UserData', 'howcanoewang@gmail.com', '1']
        dir_2 = var[5]
        dir_3 = var[6]

        if dir_1 is None:
            continue
        dir_1_final = replace_email_to_dtc(dir_1, sys_str)
        dir_2_final = replace_email_to_dtc(dir_2, sys_str)
        dir_3_final = replace_email_to_dtc(dir_3, sys_str)

        changed_record = tuple(list(var[0:4]) + [dir_1_final,dir_2_final,dir_3_final] + list(var[7:]))

        db2.execute(sql_user, changed_record)


    db2.commit()
    db1.close()
    db2.close()