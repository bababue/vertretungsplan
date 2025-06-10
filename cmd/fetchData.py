import requests
from datetime import datetime
import html
import re
import psycopg2
import os
import sys


def main():
    #connection = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
    connection = psycopg2.connect(os.environ['DATABASE_URL'])

    prepareDB(connection)

    offset_1:int = 0
    offset_2:int = 1
    if len(sys.argv) == 3:
        offset_1 = int(sys.argv[1])
        offset_2 = int(sys.argv[2])

    for r in range(offset_1, offset_2):
        updateData(r, connection)
        connection.commit()



def prepareDB(connection):
    cursor = connection.cursor()

    cursor.execute("SELECT EXISTS ( SELECT 1 FROM information_schema.tables WHERE table_name = 'vertretung') AS table_existence;")

    if (not cursor.fetchone()[0]):
        print("Table 'vertretung' not found... \nCreating it now")
        cursor.execute("""
            CREATE TABLE vertretung (
                id SERIAL PRIMARY KEY,
                datum DATE NOT NULL,
                stunde VARCHAR(50) NOT NULL,
                kurs VARCHAR(50) NOT NULL,
                raum VARCHAR(50) NOT NULL,
                lehrer VARCHAR(50) NOT NULL,
                typ VARCHAR(50),
                beschreibung VARCHAR(100)
            );
            """)
        connection.commit()
        print("Table creation completed!")
    else:
        print("Table 'vertretung' found")



def updateData(offset: int, connection):

    current_date = int(datetime.now().strftime("%Y%m%d"))
    request_config = {
        "url": "https://kephiso.webuntis.com/WebUntis/monitor/substitution/data",
        "params": {"school": "BBS Friesoythe"},
        "headers": {"content-type": "application/json"},
        "json_data": {
            "formatName": "Vertretung heute",
            "schoolName": "BBS Friesoythe",
            "date": current_date,
            "dateOffset": offset,
            "strikethrough": True,
            "mergeBlocks": True,
            "showOnlyFutureSub": True,
            "showBreakSupervisions": False,
            "showTeacher": True,
            "showClass": False,
            "showHour": True,
            "showInfo": True,
            "showRoom": True,
            "showSubject": False,
            "groupBy": 1,
            "hideAbsent": True,
            "departmentIds": [],
            "departmentElementType": -1,
            "hideCancelWithSubstitution": True,
            "hideCancelCausedByEvent": False,
            "showTime": False,
            "showSubstText": True,
            "showAbsentElements": [
                1,
                2,
            ],
            "showAffectedElements": [
                1,
                2,
            ],
            "showUnitTime": True,
            "showMessages": True,
            "showStudentgroup": False,
            "enableSubstitutionFrom": True,
            "showSubstitutionFrom": 1700,
            "showTeacherOnEvent": False,
            "showAbsentTeacher": True,
            "strikethroughAbsentTeacher": True,
            "activityTypeIds": [],
            "showEvent": False,
            "showCancel": True,
            "showOnlyCancel": False,
            "showSubstTypeColor": False,
            "showExamSupervision": False,
            "showUnheraldedExams": False,
        }
    }

    response = requests.post(
        request_config["url"],
        params=request_config["params"],
        headers=request_config["headers"],
        json=request_config["json_data"],
    )

    if response.status_code == 200:
        json_response = response.json()

        #If response contains content of next date, change date to that
        if json_response["payload"]["showingNextDate"] == True:
            json_response["payload"]["date"] = json_response["payload"]["nextDate"]

        print(f'Fetched {len(json_response["payload"]["rows"])} entries, Date: {json_response["payload"]["date"]}')
    else:
        response.raise_for_status()
        exit()



    datum = datetime.strptime(str(json_response["payload"]["date"]), "%Y%m%d").strftime("%Y-%m-%d")

    cursor = connection.cursor()
    cursor.execute(
        f"""
        DELETE FROM vertretung
        WHERE datum = '{datum}';
        """
        )

    for item in json_response["payload"]["rows"]:
        remove_html_tags = re.compile(r"<.*?>")  # Regex for removing html tags


        kurs = item["group"]

        stunde = item["data"][0]

        if item["data"][3] != "":
            typ = html.unescape(item["data"][3]) #Create a varirable for the escaped "Typ"
        else:
            typ = None

        if item["data"][4] != "":
            beschreibung = html.unescape(item["data"][4])
        else:
            beschreibung = None

        raum = re.sub(remove_html_tags, "", item["data"][1])
        if typ != None:
            if "Entfall" in typ or "Verlegung nach" in typ:
                raum= f"--- ({raum})"

        lehrer = re.sub(remove_html_tags, "", item["data"][2])
        if typ != None:
            if "Entfall" in typ or "Verlegung nach" in typ:
                lehrer= f"--- ({lehrer})"

        query = """
                INSERT INTO vertretung (datum, stunde, kurs, raum, lehrer, typ, beschreibung)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
        values = [
                datum,
                stunde,
                kurs,
                raum,
                lehrer,
                typ,
                beschreibung
                ]
        cursor.execute(query, values)


if __name__ == "__main__":
    main()
