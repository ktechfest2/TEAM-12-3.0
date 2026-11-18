from fastapi import APIRouter

from clarion_api.api.schemas import SmsSizeIn, SmsSizeOut
from clarion_api.services.rendering.sms import measure

router = APIRouter(prefix="/tools", tags=["tools"])


@router.post("/sms-size", operation_id="measureSms")
async def sms_size(body: SmsSizeIn) -> SmsSizeOut:
    size = measure(body.text)
    return SmsSizeOut(
        encoding=size.encoding,
        units=size.units,
        segments=size.segments,
        per_segment_limit=size.per_segment_limit,
    )
