from .api import task, result, oauth2, tvi


def created_routes(app):

    app.include_router(task.router, prefix="/api/task", tags=["Task Google Earth Engine"])
    app.include_router(result.router, prefix="/api/result", tags=["Result Google Earth Engine"])
    app.include_router(tvi.routes, prefix="/api/tvi", tags=["TVI - Temporal Visual Inspection"])
    app.include_router(oauth2.routes, prefix="/api/auth", tags=["Authentication"])

    return app
