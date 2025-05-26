from fastapi import HTTPException, status


async def not_found(item: any):
    UserNotFound = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(item)} not found"
    )
    return UserNotFound


async def main_exeption(item: any):
    BigProblem = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error {str(item)}"
    )

    return BigProblem
