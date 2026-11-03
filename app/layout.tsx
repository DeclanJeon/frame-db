import type { Metadata } from 'next';
import './globals.css';
export const metadata:Metadata={title:'FRAME DB — 이미지·영상 레퍼런스 데이터베이스',description:'포즈·의상 전체 색인과 24개 제작 분야의 검색·비교·연결 데이터베이스.'};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="ko"><body>{children}</body></html>}
