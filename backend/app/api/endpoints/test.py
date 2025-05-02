from fastapi import APIRouter

router = APIRouter()

@router.get("/test-connection")
async def test_connection():
    """
    Endpoint đơn giản để kiểm tra kết nối
    """
    return {
        "message": "Kết nối thành công với backend!",
        "status": "success"
    } 