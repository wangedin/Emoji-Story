import click
import random

from emoji_story import app, db
from emoji_story.blueprints.main_page import Emoji
from emoji_story.models import Post, Author, Comment


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        click.confirm('This operation will delete the database, do you want to continue?', abort=True)
        db.drop_all()
        click.echo('Drop tables.')
    db.create_all()
    click.echo('Initialized database.')


@app.cli.command()
@click.option('--count', default=20, help='Quantity of messages, default is 20.')
def forge(count):
    """Generate fake messages."""
    from faker import Faker

    db.drop_all()
    db.create_all()

    fake = Faker()
    click.echo('Working...')

    #  创建管理员
    admin = Author(
        email='admin@admin.com',
        username='Admin',
        bio=fake.text(max_nb_chars=130)
    )
    admin.set_password('12345678')
    db.session.add(admin)

    #  创建管理员名下文章
    for i in range(10):
        record = Post(
            name=admin.username,
            story=fake.paragraph(nb_sentences=5),
            time=fake.date_time_this_year(),
            emoji=Emoji.get(),
            like=random.randint(1, 1000)
        )
        admin.post.append(record)
        db.session.add(record)

    for i in range(count):
        user = Author(
            email=fake.email(),
            username=fake.user_name(),
            bio=fake.text(max_nb_chars=130)
        )
        user.set_password(fake.password())
        db.session.add(user)

        for j in range(5):
            record = Post(
                name=user.username,
                story=fake.paragraph(nb_sentences=5),
                time=fake.date_time_this_year(),
                emoji=Emoji.get(),
                like=random.randint(1, 1000)
            )
            db.session.add(record)
            user.post.append(record)

            comment = Comment(
                body=fake.paragraph(nb_sentences=5),
                time=fake.date_time_this_year(),
            )
            db.session.add(comment)
            user.comment.append(comment)
            record.comment.append(comment)

    db.session.commit()

    click.echo('Created %d fake messages.' % count)
