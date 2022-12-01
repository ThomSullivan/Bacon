import csv

from routes.models import Person, Movie, Step

def run():
    fhand = open('routes/data2.csv')
    print('Open')
    reader = csv.reader(fhand)

    #Person.objects.all().delete()
    #Movie.objects.all().delete()
    #Step.objects.all().delete()


    #kb = Person(name=4724)
    #kb.save()
    #next(reader)



    for row in reader:
        print(row[0])
        p = Person(name=row[0])
        p.bacon_number='6'
        p.save()
        m = Movie(title=row[2])
        m.save()
        #p, created = Person.objects.get_or_create(name=row[0])
        #m, created = Movie.objects.get_or_create(title=row[2])
        try:
            ns = Person.objects.get(name=row[1])
        except:
            ns = Person.objects.filter(name=row[1])[0]
        s = Step(person=p, movie=m, next_step=ns)
        s.save()




