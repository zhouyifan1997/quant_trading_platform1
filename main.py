#!/usr/bin/python3

from models.verification_model.verification_model import *
from script.database_script.database_script import *
from server.server import *

import sys

if __name__ == "__main__":
    if len(sys.argv) == 1:
        server = Server()
        server.run()
        exit(0)
    
    args = sys.argv

    if args[1] == 'database':
        database_generator = DatabaseGenerator()
        if len(args) == 2:
            print('Please provide database action')
            exit(0)
        if args[2] == 'insert':
            if len(args) == 3:
                print('Please provide stock code')
                exit(0)
            elif args[3] == 'list':
                if len(args) == 4:
                    print('Please provide file name')
                else:
                    database_generator.insert_stock_list(args[4])
            else:
                database_generator.insert_stock(args[3])
        elif args[2] == 'update':
            database_generator.update_database()
        elif args[2] == 'create':
            database_generator.generate_database()
        elif args[2] == 'drop':
            database_generator.drop_database()
    elif args[1] == 'verify':
        verification_model = VerificationModel()
        verification_model.run_test()
    elif args[1] == 'manual':
        if len(args) == 2:
            print('Please provide file name')
        file_name = args[2]
        database_generator = DatabaseGenerator()
        database_generator.determine_manual_list(file_name)