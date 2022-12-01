import csv

from routes.models import Person, Movie, Step

def run():
    fhand = open('routes/fourth_degree.csv')
    print('Open')
    reader = csv.reader(fhand)








    for row in reader:
        print(row[0])
        try:
            p = Person.objects.get(name=row[0])
        except:
            p = Person.objects.filter(name=row[0])[0]
        p.bacon_number='4'
        p.save()

