#!/usr/bin/python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from library_database_setup import MyLibrary, Base, MyBook, User

engine = create_engine('postgresql://Spiderman:freddy03@localhost:5432/mylibrary')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
# Create dummy user
User1 = User(name="William Conover", email="prchrbill@gmail.com",
             picture='https://mattcbr.files.wordpress.com/2006/09/hof002.jpg')
session.add(User1)
session.commit()


mylibrary1 = MyLibrary(user_id=1, name="Conover's Books")
session.add(mylibrary1)
session.commit()


myBook1 = MyBook(user_id=1, title="In His Steps", description="In His Steps is a most unusual appeal to the Christian to follow in Christ's steps, regardless of what others might do.", catalog="Christian Fiction", author="Charles Monroe Sheldon", mylibrary=mylibrary1)

session.add(myBook1)
session.commit()

myBook2 = MyBook(user_id=1, title="The Lord of the Rings: The Fellowship of the Ring", description="In ancient times the Rings of Power were crafted by the Elven-smiths, and Sauron, the Dark Lord, forged the One Ring, filling it with his own power so that he could rule all others. But the One Ring was taken from him, and though he sought it throughout Middle-earth, it remained lost to him. After many ages it fell into the hands of Bilbo Baggins, as told in The Hobbit. In a sleepy village in the Shire, young Frodo Baggins finds himself faced with an immense task, as his elderly cousin Bilbo entrusts the Ring to his care. Frodo must leave his home and make a perilous journey across Middle-earth to the Cracks of Doom, there to destroy the Ring and foil the Dark Lord in his evil purpose.", catalog = "Fantasy", author = "J.R.R Tolkien", mylibrary = mylibrary1)

session.add(myBook2)
session.commit()


myBook3 = MyBook(user_id=1, title="The Hobbit", description="A great modern classic and the prelude to THE LORD OF THE RINGS. Bilbo Baggins is a hobbit who enjoys a comfortable, unambitious life, rarely traveling any farther than his pantry or cellar. But his contentment is disturbed when the wizard Gandalf and a company of dwarves arrive on his doorstep one day to whisk him away on an adventure. They have launched a plot to raid the treasure hoard guarded by Smaug the Magnificent, a large and very dangerous dragon. Bilbo reluctantly joins their quest, unaware that on his journey to the Lonely Mountain he will encounter both a magic ring and a frightening creature known as Gollum.", catalog = "Fantasy", author = "J.R.R Tolkien", mylibrary = mylibrary1)

session.add(myBook3)
session.commit()


myBook4 = MyBook(user_id=1, title = "Systematic Theology: An Introduction to Biblical Doctrine", description = "The Christian church has a long tradition of systematic theology, that is, studying theology and doctrine organized around fairly standard categories such as the Word of God, redemption, and Jesus Christ. This introduction to systematic theology has several distinctive features: - A strong emphasis on the scriptural basis for each doctrine and teaching - Clear writing, with technical terms kept to a minimum - A contemporary approach, treating subjects of special interest to the church today - A friendly tone, appealing to the emotions and the spirit as well as the intellect - Frequent application to life - Resources for worship with each chapter - Bibliographies with each chapter that cross-reference subjects to a wide range of other systematic theologies.", catalog = "Christian Theology", author = "Wayne Grudem", mylibrary = mylibrary1)

session.add(myBook4)
session.commit()


myBook5 = MyBook(user_id=1, title = "The Potter's Freedom: A Defense of the Reformation and a Rebuttal To Norman Geisler's Chosen But Free", description = "This book is written as a reply to Dr. Geisler, but is much more; it is a defense of the very principles upon which the Protestant Reformation was founded. Indeed, it is a defense of the very gospel itself! In a style that both scholars and layman can appreciate, James White masterfully counters the evidence against so-called 'extreme Calvinism', defines what the Reformed Faith actually is, and concludes that the gospel preached by the Reformers is the very one taught in the pages of Scripture.", catalog = "Christian Theology", author = "James R. White", mylibrary = mylibrary1) 

session.add(myBook5)
session.commit()


myBook6 = MyBook(user_id=1, title = "Darwin's Black Box: The Biochemical Challenge to Evolution", description = "In 1996, Darwin's Black Box helped to launch the intelligent design movement: the argument that nature exhibits evidence of design, beyond Darwinian randomness. It sparked a national debate on evolution, which continues to intensify across the country. From one end of the spectrum to the other, Darwin's Black Box has established itself as the key intelligent design text -- the one argument that must be addressed in order to determine whether Darwinian evolution is sufficient to explain life as we know it.", catalog = "Science", author = "Michael J. Behe", mylibrary = mylibrary1) 

session.add(myBook6)
session.commit()


print "added your books!"
