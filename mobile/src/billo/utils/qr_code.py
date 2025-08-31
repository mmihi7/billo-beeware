import io
import base64
import segno
from typing import Optional, Tuple

class QRCodeGenerator:
    @staticmethod
    def generate_qr_code(data: str, scale: int = 10, border: int = 1) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Generate a QR code and return it as bytes and base64 string
        
        Args:
            data: The data to encode in the QR code
            scale: Scaling factor for the QR code (default: 10)
            border: Border size in modules (default: 1)
            
        Returns:
            Tuple containing (qr_bytes, qr_base64)
        """
        try:
            # Create QR code
            qr = segno.make_qr(data)
            
            # Create in-memory buffer
            buffer = io.BytesIO()
            
            # Save QR code to buffer as PNG
            qr.save(buffer, kind='png', scale=scale, border=border)
            
            # Get bytes and base64 representation
            qr_bytes = buffer.getvalue()
            qr_base64 = base64.b64encode(qr_bytes).decode('utf-8')
            
            return qr_bytes, qr_base64
            
        except Exception as e:
            print(f"Error generating QR code: {str(e)}")
            return None, None
    
    @staticmethod
    def generate_qr_code_file(data: str, filename: str, scale: int = 10, border: int = 1) -> bool:
        """
        Generate a QR code and save it to a file
        
        Args:
            data: The data to encode in the QR code
            filename: Output filename (should end with .png)
            scale: Scaling factor for the QR code (default: 10)
            border: Border size in modules (default: 1)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create QR code
            qr = segno.make_qr(data)
            
            # Save QR code to file
            qr.save(filename, scale=scale, border=border)
            return True
            
        except Exception as e:
            print(f"Error saving QR code to file: {str(e)}")
            return False
