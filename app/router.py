from .api import task, result, oauth2


def created_routes(app):

    app.include_router(task.router, prefix="/api/task", tags=["Task Google Earth Engine"])
    app.include_router(result.router, prefix="/api/result", tags=["Result Google Earth Engine"])
    app.include_router(oauth2.routes, prefix="/api/auth", tags=["Authentication"])

    return app
