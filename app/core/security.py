from fastapi import Depends, HTTPException, status

def get_current_user():
    # TODO: validate JWT; MVP stub
    return {"curator_id": "curator_001", "role": "curator"}

def require_admin(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return user
