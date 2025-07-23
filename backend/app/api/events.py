import asyncio

from sqlalchemy import event


def add_log(mapper, connection, target):
    print(f"Adding log for {target.__class__.__name__} with ID {target.id}")
    asyncio.get_running_loop().create_task(
        logar_atividade2(
            obj=target,
        )
    )


_listeners_registered = False


def add_event_listener():
    global _listeners_registered
    if _listeners_registered:
        return
    _listeners_registered = True
