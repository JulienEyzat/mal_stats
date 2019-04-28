import update_sheet as ush
import update_sqlite as usq

def transfert_sheet_sqlite(year, season):

    # The same database name for the two db
    database_name = '%s_%s' %(year, season)

    # Init GS sheet
    service = ush.get_service()
    spreadsheet_id = ush.get_spreadsheet_id(service, database_name)

    # The range of values to take (all the sheet)
    sheet_range = '%s' %(database_name)

    # Get the data from GS sheet
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_range).execute()

    # Format the data to put them in the sqlite db
    data = []
    is_first = True
    for row in result.get('values'):
        if is_first:
            anime_names = row[1:]
            is_first = False
        else:
            for index in range(len(row)):
                if index%2 == 0:
                    continue
                else:
                    data_row = {'date':row[0], 'anime_name':anime_names[index], 'anime_members':row[index], 'anime_score':row[index+1]}
                    data.append(data_row)

    # Init sqlite db
    conn, c = usq.init_connection()

    # Remove the previous table if it exists and recreate it
    usq.drop_table(c, database_name)
    usq.create_table(c, database_name)

    # Insert the new values in the database
    usq.update_table(conn, c, database_name, data)

def transfert_database(source, destination, year, season):
    if source == 'google' and destination == 'sqlite':
        transfert_sheet_sqlite(year, season)
    else:
        print('Not implemented yet')
