import os
from typing import Optional, Dict
from pydantic import BaseModel, Field

from langchain.tools import BaseTool
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
    AsyncCallbackManagerForToolRun,
)


class TimKiemKhachHangSchema(BaseModel):
    """Input schema cho tìm kiếm khách hàng"""

    phone_number: str = Field(..., description="Số điện thoại của khách hàng.")


class TimKiemKhachHangTool(BaseTool):
    name: str = "tim_kiem_khach_hang"
    description: str = (
        "Tìm kiếm khách hàng dựa trên số điện thoại. Hãy gọi công cụ này khi có thể, nếu sai ở đâu công cụ sẽ báo lại."
    )
    args_schema: type[BaseModel] = TimKiemKhachHangSchema
    return_direct: bool = False

    def _run(
        self,
        phone_number: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict:
        """Tìm kiếm khách hàng dựa trên số điện thoại. Hãy gọi công cụ này khi có thể, nếu sai ở đâu công cụ sẽ báo lại.

        Args:
            phone_number (str): Tiêu đề của tờ trình. Có thể tự tạo dựa trên loại kinh phí.

        Returns:
            Dict: Kết quả tìm kiếm khách hàng.
                - Nếu thành công: {"status": "success", "message": "Đã tìm được thông tin khách hàng.", "data": { <thông tin khách hàng> } }
                - Nếu lỗi: {"status": "error", "message": ...}
        """
        try:
            return {
                "status": "success",
                "message": "Đã tìm được thông tin khách hàng.",
                "data": {"id": "1234"},
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _arun(
        self,
        phone_number: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Dict:
        """Asynchronous execution."""
        return self._run(
            phone_number,
            run_manager=run_manager.get_sync(),
        )


class TaoCoHoiBanSchema(BaseModel):
    """Input schema cho tạo cơ hội bán"""

    customer_id: Optional[str] = Field(..., description="ID của khách hàng")
    product_name: Optional[str] = Field(..., description="Tên của sản phẩm")
    state: Optional[str] = Field(
        ..., description="Trạng thái cơ hội bán: Tiếp cận / Tư vấn / Từ chối / Thành công / Thất bại"
    )
    sale_value: Optional[int] = Field(..., description="Doanh số (đơn vị VND)")


class TaoCoHoiBanTool(BaseTool):
    name: str = "tao_co_hoi_ban"
    description: str = "Tạo cơ hội bán. Hãy gọi công cụ này khi có thể, nếu sai ở đâu công cụ sẽ báo lại."
    args_schema: type[BaseModel] = TaoCoHoiBanSchema
    return_direct: bool = False

    def _run(
        self,
        customer_id: Optional[str],
        product_name: Optional[str],
        state: Optional[str],
        sale_value: Optional[int],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict:
        """Tạo cơ hội bán lên hệ thống. Hãy gọi công cụ này khi có thể, nếu sai ở đâu công cụ sẽ báo lại.

        Args:
            customer_id (Optional[str], optional): ID của khách hàng
            product_name (Optional[str], optional): Tên của sản phẩm
            state (Optional[str], optional): Trạng thái cơ hội bán: Tiếp cận / Tư vấn / Từ chối / Thành công / Thất bại
            sale_value (Optional[int], optional): Doanh số (đơn vị VND)

        Returns:
            Dict: Kết quả tạo cơ hội bán.
                - Nếu thành công: {"status": "success", "message": "Đã tạo thành công cơ hội bán.", "data": { <thông tin cơ hội bán> } }
                - Nếu lỗi: {"status": "error", "message": ...}
        """
        try:
            return {
                "status": "success",
                "message": "Đã tạo thành công cơ hội bán.",
                "data": {},
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _arun(
        self,
        customer_id: Optional[str],
        product_name: Optional[str],
        state: Optional[str],
        sale_value: Optional[int],
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Dict:
        """Asynchronous execution."""
        return self._run(
            customer_id,
            product_name,
            state,
            sale_value,
            run_manager=run_manager.get_sync(),
        )
