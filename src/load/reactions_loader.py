"""
Reactions Loader Module

This module handles loading and parsing LLM-analyzed reactions from markdown files
for integration into the Rick Steves Audio Guide Dashboard.
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import streamlit as st

# Hardcoded Korean translations for each museum
KOREAN_TRANSLATIONS = {
    "British Museum": {
        "overall_summary": "대영박물관의 오디오 가이드는 전반적으로 긍정적인 피드백을 받고 있으며, 많은 방문객들이 박물관의 방대한 소장품을 탐색하는 데 유용한 도구로 여기고 있습니다. Rick Steves 오디오 가이드는 하이라이트 투어를 위한 인기 있는 무료 옵션입니다. 그러나 박물관의 엄청난 규모와 혼잡한 특성으로 인해 어떤 오디오 가이드든 효과적으로 사용하기 어려울 수 있습니다.",
        "positive_points": [
            "어린이용 오디오 가이드는 특히 호평을 받고 있으며, 한 사용자는 '성인에게도 꽤 흥미롭다'고 언급했습니다.",
            "Rick Steves 오디오 가이드는 박물관 하이라이트의 '매우 높은 수준' 투어를 위한 인기 있는 무료 옵션입니다.",
            "오디오 가이드는 소장품에 대한 개요를 얻고 이렇게 큰 박물관 방문을 최대한 활용하는 좋은 방법으로 여겨집니다.",
            "박물관은 또한 오디오 앱을 제공하여 기기 대여의 편리한 대안을 제공합니다."
        ],
        "negative_points": [
            "박물관의 엄청난 규모와 종종 '극도로 혼잡한' 특성으로 인해 오디오 가이드를 따라가기 어려울 수 있습니다.",
            "한 사용자는 너무 많은 유물로 인해 집중하기 어려워서 박물관이 '압도적이고 약간 지루하다'고 느꼈습니다.",
            "또 다른 사용자는 많은 것들이 이동되어 가이드북의 설명과 더 이상 일치하지 않아서 '약간 길을 잃었다'고 보고했습니다."
        ],
        "recommendation": "대영박물관 방문 시, 미리 계획을 세우고 주요 관심 영역을 식별하는 것이 좋습니다. Rick Steves 오디오 가이드는 집중된 하이라이트 투어에 좋은 옵션입니다. 방문객들은 혼잡함과 박물관의 레이아웃이 오디오 가이드와 완벽하게 일치하지 않을 가능성에 대비해야 합니다."
    },
    "Louvre Museum": {
        "overall_summary": "루브르 박물관 오디오 가이드에 대한 사용자 피드백은 혼재되어 있으며, 공식 박물관 가이드와 무료 Rick Steves 오디오 투어 간의 만족도에 현저한 차이가 있습니다. 공식 루브르 오디오 가이드는 일반적으로 호평을 받고 있습니다. 방문객들은 이를 광대하고 종종 압도적인 박물관을 탐색하는 데 유용한 도구로 여깁니다. 예술사에 대한 강한 배경지식이 없는 사람들에게 특히 권장되며, 경험을 더욱 흥미롭고 정보가 풍부하게 만드는 데 도움이 됩니다. 반면, Rick Steves 오디오 가이드는 더 비판적인 피드백을 받습니다. 주요 불만은 박물관의 빈번한 전시 재구성으로 인해 가이드가 구식이라는 것입니다. 이로 인해 많은 사용자들이 예술작품이 더 이상 설명된 위치에 있지 않아 투어를 따라가기 어렵다고 느끼고 있습니다.",
        "positive_points": [
            "박물관 경험을 향상시키며, 특히 비전문가에게 좋습니다.",
            "방대한 소장품을 탐색하고 하이라이트의 구조화된 투어를 제공하는 데 도움이 됩니다.",
            "일반적으로 품질이 좋고 대여료의 가치가 있다고 여겨집니다."
        ],
        "negative_points": [
            "박물관 레이아웃의 변화로 인해 자주 구식이 됩니다.",
            "따라가기 어렵고 좌절스러울 수 있습니다.",
            "여러 사용자가 공식 박물관 가이드를 선택하지 않은 것을 후회한다고 표현했습니다."
        ],
        "recommendation": "더 신뢰할 수 있고 덜 좌절스러운 경험을 위해 공식 루브르 오디오 가이드가 권장됩니다. Rick Steves 가이드를 사용할 계획이라면, 박물관의 현재 레이아웃과 완벽하게 일치하지 않을 가능성에 대비해야 합니다."
    },
    "Museo del Prado": {
        "overall_summary": "프라도 박물관의 오디오 가이드는 일반적으로 그 내용에 대해 칭찬받지만, 사용자 피드백은 가용성과 신뢰성에 상당한 문제가 있음을 보여줍니다. 프라도에는 Rick Steves 오디오 가이드가 없는데, 이는 많은 사람들에게 실망의 원인이 됩니다. 박물관 자체 가이드는 접근 가능할 때 유용한 도구로 여겨집니다.",
        "positive_points": [
            "오디오 가이드의 내용은 큰 박물관을 탐색하는 데 '매우 유용'하고 '매우 좋다'고 여겨집니다.",
            "프라도는 물리적 기기 대여의 대안을 제공하는 공식 앱 'The Prado Guide'를 제공합니다.",
            "가이드는 박물관의 하이라이트인 '상위 50개' 작품에 집중하고 싶은 방문객에게 도움이 됩니다."
        ],
        "negative_points": [
            "가장 중요한 문제는 일부 사용자들이 보고한 상설 전시 오디오 가이드의 가용성 부족입니다.",
            "대여 기기의 신뢰성에 대한 우려가 있으며, 한 사용자는 근처 El Escorial의 오디오 가이드 배터리가 전체 투어를 지속하기에 너무 약했다고 보고했습니다.",
            "Rick Steves 오디오 가이드 부족은 그의 투어 팬들에게 흔한 좌절의 원인입니다."
        ],
        "recommendation": "프라도 방문 전에 오디오 가이드 가용성의 현재 상태를 확인하기 위해 공식 박물관 웹사이트를 확인하는 것을 강력히 권장합니다. 가이드가 사용 가능하다면 박물관의 방대한 소장품을 탐색하는 데 가치 있는 투자입니다. 대안으로 방문객들은 스마트폰에 공식 프라도 앱을 다운로드할 수 있습니다."
    },
    "Tate Modern": {
        "overall_summary": "테이트 모던의 오디오 가이드에 대한 피드백은 혼재되어 있으며, 상당한 수의 방문객들이 좌절과 실망을 표현하고 있습니다. 일부 사용자는 가이드가 도움이 된다고 느끼지만, 특히 현대 예술에 대한 특별한 관심이 있는 사람들에게는 그렇습니다. 다른 사람들은 사용하기 어렵고 박물관의 조직이 혼란스럽다고 느낍니다.",
        "positive_points": [
            "예술가 Joseph Beuys의 팬인 한 사용자는 오디오 가이드가 '매우 도움이 된다'고 느꼈습니다.",
            "오디오 가이드는 London Pass로 무료로 이용할 수 있어 패스 소지자에게는 보너스입니다."
        ],
        "negative_points": [
            "가장 중요한 비판은 오디오 가이드가 '파악하기 매우 어렵다'는 것으로, 사용자 친화성 부족을 시사합니다.",
            "이 어려움은 투어를 따라가기 어렵게 만드는 박물관의 '어려운' 조직으로 인해 더욱 악화된다고 보고됩니다.",
            "한 사용자는 6명 전체 그룹이 '테이트 모던에 실망했다'고 보고했는데, 이는 오디오 가이드를 넘어선 전반적으로 나쁜 경험을 나타냅니다."
        ],
        "recommendation": "테이트 모던 방문객들은 오디오 가이드와 함께 혼란스럽고 좌절스러운 경험의 가능성을 인식해야 합니다. 가이드는 현대 예술에 대한 강한 기존 관심이 있는 사람들에게 더 유익할 수 있습니다. 전시품을 더 잘 탐색하기 위해 박물관의 레이아웃과 소장품을 미리 조사하는 것이 도움이 될 수 있습니다."
    },
    "Uffizi Gallery": {
        "overall_summary": "우피치 갤러리의 오디오 가이드는 혼재된 평가를 받고 있습니다. 많은 방문객들이 박물관을 탐색하고 예술을 이해하는 데 도움이 된다고 느끼지만, 상당한 수의 사용자들이 부정적인 경험을 했으며, 특히 Rick Steves 오디오 가이드와 관련하여 그렇습니다. 주요 문제는 박물관의 지속적인 리모델링과 그로 인한 레이아웃 변화로 인해 오디오 가이드를 따라가기 어렵다는 것입니다.",
        "positive_points": [
            "공식 우피치 오디오 가이드는 '매우 좋고 매우 철저하다'고 설명되며, 예술에 대한 깊은 관심이 있는 사람들에게 권장됩니다.",
            "박물관은 소액의 비용으로 이용할 수 있는 '좋은 오디오 가이드'가 있는 앱을 제공합니다.",
            "Rick Steves 오디오 가이드는 무료이고 하이라이트에 대한 좋은 개요를 제공한다는 점에서 칭찬받지만, 따라갈 수 있을 때만 그렇습니다."
        ],
        "negative_points": [
            "가장 흔한 불만은 박물관의 리모델링으로 인해 Rick Steves 오디오 가이드가 구식이 되어 혼란스럽고 사용하기 어렵다는 것입니다.",
            "박물관의 레이아웃이 혼란스러울 수 있으며, 지속적인 변화로 인해 어떤 가이드든 따라가기 어렵습니다.",
            "편의를 제공하기로 한 Firenze Card는 항상 줄을 건너뛸 수 있게 해주지 않아 '번거로움'이 될 수 있으며, 오디오 가이드를 받기 위해 여전히 줄을 서야 할 수도 있습니다."
        ],
        "recommendation": "우피치의 지속적인 리모델링으로 인해 공식 박물관 오디오 가이드나 우피치 앱이 Rick Steves 오디오 가이드보다 더 신뢰할 수 있고 최신일 가능성이 높습니다. 레이아웃과 이용 가능한 투어나 가이드에 대한 최신 정보를 위해 방문 전에 박물관의 공식 웹사이트를 확인하는 것을 강력히 권장합니다."
    }
}

class ReactionsLoader:
    """Load and parse LLM-analyzed reactions from markdown files."""
    
    def __init__(self, reactions_dir: str = "."):
        """Initialize with reactions directory path."""
        self.reactions_dir = Path(reactions_dir)
        self.reactions_data = {}
        self.load_reactions()
    
    def load_reactions(self) -> None:
        """Load all reactions markdown files."""
        # Define museum name mappings
        museum_mappings = {
            "british_museum": "British Museum",
            "louvre": "Louvre Museum", 
            "prado": "Museo del Prado",
            "tate_modern": "Tate Modern",
            "uffizi": "Uffizi Gallery"
        }
        
        for filename, museum_name in museum_mappings.items():
            file_path = self.reactions_dir / f"{filename}_audio_guide_reactions.md"
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    parsed_data = self.parse_reactions_content(content, museum_name)
                    
                    # Add Korean translations from hardcoded data
                    if museum_name in KOREAN_TRANSLATIONS:
                        ko_data = KOREAN_TRANSLATIONS[museum_name]
                        parsed_data['ko_overall_summary'] = ko_data.get('overall_summary', '')
                        parsed_data['ko_positive_points'] = ko_data.get('positive_points', [])
                        parsed_data['ko_negative_points'] = ko_data.get('negative_points', [])
                        parsed_data['ko_recommendation'] = ko_data.get('recommendation', '')
                    
                    self.reactions_data[museum_name] = parsed_data
                    
                except Exception as e:
                    if hasattr(st, 'runtime') and st.runtime.exists():
                        st.warning(f"Could not load reactions for {museum_name}: {e}")
                    else:
                        print(f"Could not load reactions for {museum_name}: {e}")
    
    def parse_reactions_content(self, content: str, museum_name: str) -> Dict[str, Any]:
        """Parse markdown content into structured data."""
        parsed = {
            "museum": museum_name,
            "overall_summary": "",
            "positive_points": [],
            "negative_points": [],
            "recommendation": "",
            "raw_content": content
        }
        
        # Extract overall summary
        summary_match = re.search(r'## Overall Summary\s*\n\s*(.*?)(?=\n##|\n\*\*|$)', 
                                content, re.DOTALL)
        if summary_match:
            parsed["overall_summary"] = summary_match.group(1).strip()
        
        # Extract positive points - handle both formats
        positive_patterns = [
            r'\*\*Positive:\*\*\s*\n(.*?)(?=\n\*\*Negative:\*\*|\n\*\*Recommendation:\*\*|$)',
            r'\*\*Positive \(Official Guide\):\*\*\s*\n(.*?)(?=\n\*\*Negative|\n\*\*General|\n\*\*Recommendation|\n$)',
            r'\*\*Positive:\*\*\s*\n(.*?)(?=\n\*\*Negative|\n\*\*General|\n\*\*Recommendation|\n$)'
        ]
        
        positive_points = []
        for pattern in positive_patterns:
            positive_section = re.search(pattern, content, re.DOTALL)
            if positive_section:
                positive_text = positive_section.group(1)
                # Extract bullet points
                points = re.findall(r'\*\s*(.*?)(?=\n\*\s*|\n$)', positive_text, re.DOTALL)
                positive_points.extend([point.strip() for point in points if point.strip()])
        
        parsed["positive_points"] = positive_points
        
        # Extract negative points - handle both formats
        negative_patterns = [
            r'\*\*Negative:\*\*\s*\n(.*?)(?=\n\*\*Recommendation:\*\*|$)',
            r'\*\*Negative \(Rick Steves Guide\):\*\*\s*\n(.*?)(?=\n\*\*General|\n\*\*Recommendation|\n$)',
            r'\*\*Negative:\*\*\s*\n(.*?)(?=\n\*\*General|\n\*\*Recommendation|\n$)'
        ]
        
        negative_points = []
        for pattern in negative_patterns:
            negative_section = re.search(pattern, content, re.DOTALL)
            if negative_section:
                negative_text = negative_section.group(1)
                # Extract bullet points
                points = re.findall(r'\*\s*(.*?)(?=\n\*\s*|\n$)', negative_text, re.DOTALL)
                negative_points.extend([point.strip() for point in points if point.strip()])
        
        parsed["negative_points"] = negative_points
        
        # Extract recommendation
        recommendation_match = re.search(r'\*\*Recommendation:\*\*\s*(.*?)(?=\n|$)', 
                                      content, re.DOTALL)
        if recommendation_match:
            parsed["recommendation"] = recommendation_match.group(1).strip()
        
        return parsed
    
    def get_reactions_for_museum(self, museum_name: str) -> Optional[Dict[str, Any]]:
        """Get reactions data for a specific museum."""
        # Try exact match first
        if museum_name in self.reactions_data:
            return self.reactions_data[museum_name]
        
        # Try partial matching with more flexible logic
        for key, data in self.reactions_data.items():
            # Handle special cases for museum name variations
            if any(term in museum_name.lower() for term in ['prado', 'museo del prado']) and 'prado' in key.lower():
                return data
            elif museum_name.lower() in key.lower() or key.lower() in museum_name.lower():
                return data
        
        return None
    
    def get_all_reactions(self) -> Dict[str, Any]:
        """Get all reactions data."""
        return self.reactions_data
    
    def get_museums_with_reactions(self) -> List[str]:
        """Get list of museums that have reactions data."""
        return list(self.reactions_data.keys()) 