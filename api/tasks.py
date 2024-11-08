from celery import shared_task


@shared_task
def test_task():
    print("Test task executed!")


x = 10
y = 20


@shared_task
def add():
    return x + y
