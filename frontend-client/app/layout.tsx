import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "UIndy AutoMic",
  description: "Automated microphone positioning system for UIndy Music Department by Team AutoMic",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased font-sans">
        {children}
      </body>
    </html>
  );
}
