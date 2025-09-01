#!/usr/bin/env python3
"""
Test with the user's provided Japanese team example
Tests the specific format: "努力値：H252 A4 B156 D68 S28"
"""

import sys
from pathlib import Path
import json
import os

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from core.analyzer import GeminiVGCAnalyzer

# User's provided Japanese team example
USER_EXAMPLE = """
黒バドレックス＠気合の襷
実数値：175-*-101-217-120-222
努力値：B4 C252 S252
性格：臆病　特性：人馬一体　テラス：霊
アストラルビット/サイコキネシス/アンコール/守る

調整意図
・CSぶっぱ、あまりB

変更点
　スカーフ水ウーラオスが絶滅したので、B振りをやめました。
鉢巻水流連打を耐えるB204振りは検討したものの、さすがに火力不足に困る方が多そうだったのでこれもやめました。

　先月から変わらない本構築のエース、最強の伝説枠です。
今までは全ての試合で後発させていたのですが、カイリューが加入したことで削り役として先発起用する選出もできるようになりました。



ザマゼンタ＠朽ちた盾
実数値：199-141-198-*-169-152
努力値：H252 A4 B156 D68 S28
性格：腕白　特性：不屈の盾　テラス：水
ボディプレス/ヘビーボンバー/ワイドガード/守る

調整意図
・黒バドのC+2珠サイキネを93.6%耐える
・最速テラパゴス+2
・残りB

変更点
　BSを削り、特殊耐久を厚くしましたが、結果的にこれは失敗でした。最終日にはドーブル入り黒バド+ザマゼンタが消滅していた一方、ザマゼンタとの対戦があまりにも多かったため、Sをガンガンに上げてザマゼンタミラーで上を取りに行くべきでした。
　またBを削ってしまった弊害として、災いボディプレス+不意打ちで水ウーラオスを処理できる確率がかなり怪しくなってしまいました。



パオジアン＠突撃チョッキ
実数値：179-140-100-*-110-188
努力値：H188 D196 S124
性格：陽気　特性：災いの剣　テラス：水
カタストロフィ/アイススピナー/不意打ち/氷の礫

調整意図
・準速135族（ミライドン・パオジアン）抜き
・陽気ザシアンのじゃれつくを水テラス時に93.6%耐え
・残り全てD。臆病ミライドンの電テラ（≒珠）イナドラまでは耐える

変更点
　前述のとおりスカーフ水ウーラを誰も使わなくなったので、B方面を落としてDに回しました。実際にスカーフ電テライナドラから生還して勝利した試合があり、奏功しました。並びを変更したことでチョッキパオジアンであることがまたバレにくくなっていたようにも感じました。
　カイリューが加入したことで黒バドの先発が増え、その際の引き先としてパオジアンを選択することが多かったです。
　なお変更点ではありませんが補足として。パオジアンのテラスはトルネ+ザシアンor水ウーラなど残数を取られてはいけない対戦で切ります。両方に有効な水テラスです。



モロバレル＠メンタルハーブ
実数値：219-*-129-105-107-31
努力値：H236 B220 D52
性格：呑気　特性：再生力　テラス：水
ヘドロ爆弾/怒りの粉/キノコの胞子/守る

調整意図
・意地パオジアンの氷柱落としを93.6%耐え
・控えめミライドンの流星群を93.6％耐え
・最遅

変更点
　唯一の変更なし。先月は無理そうな構築全部に渋々選出されていましたが、今月はカイリューという選択肢ができたので、だいぶ適正な選出率に落ち着いたように思います。



カイリュー＠拘り鉢巻
実数値：197-204-116-*-121-101
努力値：H244 A252 B4 D4 S4
性格：意地　特性：精神力　テラス：無
神速/けたぐり/岩雪崩/逆鱗

調整意図
"""

def test_user_example():
    """Test the user's provided Japanese team example"""
    print("=== TESTING USER'S JAPANESE TEAM EXAMPLE ===")
    print("Testing enhanced EV detection with hybrid format:")
    print("- Pattern: B4 C252 S252")
    print("- Pattern: H252 A4 B156 D68 S28")  
    print("- Pattern: H188 D196 S124")
    print("- etc.")
    
    try:
        analyzer = GeminiVGCAnalyzer()
        
        print(f"\nAnalyzing content ({len(USER_EXAMPLE)} characters)...")
        result = analyzer.analyze_article(USER_EXAMPLE)
        
        if not result:
            print("ERROR: No analysis result returned")
            return False
            
        # Check Pokemon team
        pokemon_team = result.get("pokemon_team", [])
        print(f"Pokemon detected: {len(pokemon_team)}")
        
        if not pokemon_team:
            print("ERROR: No Pokemon team detected")
            return False
            
        # Expected EV patterns from the user's example
        expected_evs = [
            {"name": "Calyrex-Shadow", "pattern": "B4 C252 S252", "total": 508},  # 黒バドレックス
            {"name": "Zamazenta", "pattern": "H252 A4 B156 D68 S28", "total": 508},
            {"name": "Chien-Pao", "pattern": "H188 D196 S124", "total": 508},  # パオジアン
            {"name": "Amoonguss", "pattern": "H236 B220 D52", "total": 508},   # モロバレル
            {"name": "Dragonite", "pattern": "H244 A252 B4 D4 S4", "total": 508}, # カイリュー
        ]
        
        complete_count = 0
        ev_matches = 0
        
        for i, pokemon in enumerate(pokemon_team, 1):
            name = pokemon.get('name', 'Unknown')
            
            # Check EV spread
            ev_spread = pokemon.get('ev_spread', {})
            ev_total = ev_spread.get('total', 0) if ev_spread else 0
            has_evs = ev_total > 0
            
            # Check other data
            held_item = pokemon.get('held_item', pokemon.get('item', 'None'))
            has_item = held_item and held_item not in ["Unknown", "None", None, "Not specified"]
            has_moves = len(pokemon.get('moves', [])) >= 4
            has_ability = pokemon.get('ability') and pokemon.get('ability') != "Unknown"
            
            print(f"\n  Pokemon {i}: {name}")
            print(f"    EV Spread: {has_evs} (Total: {ev_total})")
            if has_evs and ev_spread:
                hp = ev_spread.get('HP', 0)
                atk = ev_spread.get('Attack', 0)
                def_ = ev_spread.get('Defense', 0)
                spa = ev_spread.get('Special Attack', 0)
                spd = ev_spread.get('Special Defense', 0)
                spe = ev_spread.get('Speed', 0)
                print(f"      Detail: HP{hp} A{atk} B{def_} C{spa} D{spd} S{spe}")
            print(f"    Item: {has_item} ({held_item})")
            print(f"    Moves: {has_moves} ({len(pokemon.get('moves', []))} moves)")
            print(f"    Ability: {has_ability} ({pokemon.get('ability', 'None')})")
            
            # Check if EV pattern matches expected
            for expected in expected_evs:
                if expected["name"].lower() in name.lower() or name in expected["name"]:
                    if ev_total == expected["total"]:
                        ev_matches += 1
                        print(f"    SUCCESS: EV pattern matches expected for {expected['name']}")
                        break
            
            if has_evs and has_item and has_moves and has_ability:
                complete_count += 1
                print(f"    Status: COMPLETE")
            else:
                missing = []
                if not has_evs: missing.append("EVs")
                if not has_item: missing.append("Item")
                if not has_moves: missing.append("Moves")
                if not has_ability: missing.append("Ability")
                print(f"    Status: INCOMPLETE (missing: {', '.join(missing)})")
        
        # Save results
        with open("test_user_example_results.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n=== RESULTS SUMMARY ===")
        print(f"Total Pokemon: {len(pokemon_team)}")
        print(f"Complete Pokemon: {complete_count}")
        print(f"EV Pattern Matches: {ev_matches}")
        print(f"Success Rate: {complete_count}/{len(pokemon_team)} ({100*complete_count/len(pokemon_team):.1f}%)")
        print(f"Results saved to: test_user_example_results.json")
        
        # Determine success
        success = complete_count >= len(pokemon_team) * 0.8  # 80% success threshold
        print(f"\nOVERALL: {'SUCCESS' if success else 'NEEDS IMPROVEMENT'}")
        
        return success
        
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_user_example()