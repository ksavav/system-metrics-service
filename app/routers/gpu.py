from fastapi import APIRouter, HTTPException


router = APIRouter()

@router.get("/gpu", tags=["gpu"])
async def get_total_gpu_metrics():
    pass