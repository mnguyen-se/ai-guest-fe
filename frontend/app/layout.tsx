import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Đài Quan Sát Đầu Tư",
  description: "Trợ lý AI phân tích vĩ mô, thị trường và tin tức — không dự đoán, chỉ soi chiếu bằng chứng.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi">
      <body className="antialiased">{children}</body>
    </html>
  );
}
