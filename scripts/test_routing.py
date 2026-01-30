#!/usr/bin/env python3
"""
路由測試腳本
驗證問題是否被路由到正確的 Agent
"""

import sys
import os

# 將 src 目錄加入 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.voice import ChatBot
from dotenv import load_dotenv

load_dotenv()


def test_routing():
    """測試路由準確度"""
    
    # 測試案例：(問題, 預期的Agent)
    test_cases = [
        # ==================== 數學問題 ====================
        # 基礎計算
        ("3 + 5 等於多少？", "math_tutor"),
        ("10 減 7 是多少？", "math_tutor"),
        ("5 乘以 6 等於什麼？", "math_tutor"),
        ("12 除以 3 等於多少？", "math_tutor"),
        ("什麼是分數？", "math_tutor"),
        
        # 長問題：數學概念
        ("老師說分數就是把一個東西分成好幾份，那什麼時候要用分數來表示呢？", "math_tutor"),
        ("如果我有 10 顆糖果，要平分給 5 個小朋友，每個人可以分到幾顆？", "math_tutor"),
        ("請問小數點是什麼意思？為什麼 0.5 等於二分之一？", "math_tutor"),
        ("媽媽給我 100 元，我買了一本 35 元的筆記本，還剩下多少錢？", "math_tutor"),
        
        # ==================== 科學問題 ====================
        # 自然現象
        ("為什麼天空是藍色的？", "science_tutor"),
        ("月亮為什麼會發光？", "science_tutor"),
        ("植物怎麼進行光合作用？", "science_tutor"),
        ("為什麼會下雨？", "science_tutor"),
        ("聲音是怎麼產生的？", "science_tutor"),
        
        # 長問題：科學原理
        ("我看到天空有時候是藍色，有時候是紅色，尤其是早上和晚上，這是為什麼呢？", "science_tutor"),
        ("植物沒有嘴巴，它們是怎麼吃東西的？光合作用到底是什麼意思？", "science_tutor"),
        ("為什麼冬天會下雪而不是下雨？雪和雨有什麼不一樣？", "science_tutor"),
        ("恐龍為什麼會滅絕？是因為隕石撞擊地球嗎？那其他動物為什麼沒有滅絕？", "science_tutor"),
        ("我們呼吸的時候吸進去氧氣，吐出來二氧化碳，那空氣會不會用完？", "science_tutor"),
        
        # ==================== 語文問題 ====================
        # 寫作閱讀
        ("怎麼寫好作文？", "language_tutor"),
        ("請幫我造句", "language_tutor"),
        ("這個成語是什麼意思？", "language_tutor"),
        ("如何提升閱讀理解？", "language_tutor"),
        
        # 長問題：語文學習
        ("老師說我的作文寫得很平淡，沒有生動的描寫，我應該怎麼讓作文更有趣？", "language_tutor"),
        ("我看故事書的時候，常常看完就忘記內容了，怎麼樣才能記住故事在說什麼？", "language_tutor"),
        ("用『高興』這個詞造句，而且要造一個比較長、比較有趣的句子。", "language_tutor"),
        ("什麼是修辭法？像是比喻、擬人這些，要怎麼用在作文裡面？", "language_tutor"),
        
        # ==================== 學習方法 ====================
        # 學習技巧
        ("怎麼快速記住單字？", "pedagogy"),
        ("我不會讀書怎麼辦？", "pedagogy"),
        ("如何提高專注力？", "pedagogy"),
        ("複習有什麼技巧？", "pedagogy"),
        
        # 長問題：學習策略
        ("我每次考試前都會很緊張，然後就記不住背過的東西，有什麼方法可以改善嗎？", "pedagogy"),
        ("老師說要做筆記，但我不知道應該記什麼、怎麼記，筆記本都亂七八糟的。", "pedagogy"),
        ("為什麼我上課聽得懂，但是回家寫作業就不會了？是我的學習方法有問題嗎？", "pedagogy"),
        ("每天要讀很多科目，數學、國語、自然、社會，我應該怎麼安排時間才不會讀不完？", "pedagogy"),
        
        # ==================== 答案評估 ====================
        # 檢查答案
        ("我的答案是 8，對不對？", "assessment"),
        ("這樣算對嗎？", "assessment"),
        ("請幫我檢查答案", "assessment"),
        
        # 長問題：複雜評估
        ("我算出來 25 除以 5 等於 5，但是同學說是 4，到底誰是對的？可以幫我檢查嗎？", "assessment"),
        ("老師說這題作文寫得不好，但我不知道哪裡有問題，你能幫我看看嗎？", "assessment"),
        
        # ==================== 情緒支持 ====================
        # 情緒閒聊
        ("我覺得學習好難", "companion"),
        ("今天心情不好", "companion"),
        ("你好", "companion"),
        ("謝謝你", "companion"),
        
        # 長問題：情緒表達
        ("今天考試考得很差，我覺得自己好笨，都不想再讀書了。", "companion"),
        ("班上同學都比我厲害，我覺得自己什麼都做不好，好難過。", "companion"),
        ("爸爸媽媽一直要我去補習，但我真的好累，我只想休息一下。", "companion"),
        
        # ==================== 混合型問題（較難） ====================
        # 需要精確判斷的複雜問題
        ("分數的加法和減法要怎麼算？為什麼要先通分？", "math_tutor"),  # 數學而非學習方法
        ("為什麼人要呼吸？如果不呼吸會怎樣？", "science_tutor"),  # 科學而非情緒
        ("閱讀測驗總是看不懂，是不是我的理解能力有問題？", "language_tutor"),  # 語文而非學習方法
        ("為什麼我背單字總是記不住？是記憶力不好嗎？", "pedagogy"),  # 學習方法
        ("我寫的這段話：『今天天氣很好，我很開心』，這樣對不對？", "assessment"),  # 評估
        ("老師今天罵我，我好難過，不想去學校了。", "companion"),  # 情緒而非學習
    ]
    
    print("\n" + "=" * 80)
    print("🧪 路由準確度測試（包含複雜長問題）")
    print("=" * 80)
    print(f"📊 總測試數: {len(test_cases)} 個")
    print(f"   - 基礎問題: 25 個")
    print(f"   - 複雜長問題: {len(test_cases) - 25} 個")
    print("=" * 80)
    
    # 初始化 ChatBot
    bot = ChatBot(use_multi_agent=True, save_conversation=False)
    
    if not bot.use_multi_agent or not bot.orchestrator:
        print("❌ Multi-Agent 模式未啟用")
        return
    
    # 統計
    total = len(test_cases)
    correct = 0
    results = []
    
    for question, expected_agent in test_cases:
        # 路由決策
        routing_result = bot.orchestrator.gateway.route_question(question, verbose=False)
        actual_agent = routing_result['agent']
        confidence = routing_result['confidence']
        
        # 檢查是否正確
        is_correct = (actual_agent == expected_agent)
        if is_correct:
            correct += 1
        
        # 記錄結果
        result = {
            'question': question,
            'expected': expected_agent,
            'actual': actual_agent,
            'confidence': confidence,
            'correct': is_correct,
            'keywords': routing_result.get('matched_keywords', [])
        }
        results.append(result)
        
        # 顯示結果
        status = "✅" if is_correct else "❌"
        print(f"\n{status} 問題: {question}")
        print(f"   預期: {expected_agent}")
        print(f"   實際: {actual_agent} (信心度: {confidence:.0%})")
        if routing_result.get('matched_keywords'):
            print(f"   關鍵字: {', '.join(routing_result['matched_keywords'])}")
        
        if not is_correct:
            print(f"   ⚠️  路由錯誤！")
    
    # 顯示統計
    accuracy = (correct / total) * 100
    print("\n" + "=" * 80)
    print(f"📊 測試結果統計")
    print("=" * 80)
    print(f"總測試數: {total}")
    print(f"正確數: {correct}")
    print(f"錯誤數: {total - correct}")
    print(f"準確率: {accuracy:.1f}%")
    
    # 按 Agent 統計
    print(f"\n📈 各 Agent 準確率:")
    agent_stats = {}
    for result in results:
        agent = result['expected']
        if agent not in agent_stats:
            agent_stats[agent] = {'total': 0, 'correct': 0}
        agent_stats[agent]['total'] += 1
        if result['correct']:
            agent_stats[agent]['correct'] += 1
    
    for agent, stats in sorted(agent_stats.items()):
        acc = (stats['correct'] / stats['total']) * 100
        print(f"   {agent:20s}: {stats['correct']}/{stats['total']} ({acc:.0f}%)")
    
    # 顯示錯誤案例
    errors = [r for r in results if not r['correct']]
    if errors:
        print(f"\n❌ 錯誤案例分析 ({len(errors)} 個):")
        for err in errors:
            print(f"\n   問題: {err['question']}")
            print(f"   預期 Agent: {err['expected']}")
            print(f"   實際 Agent: {err['actual']}")
            print(f"   信心度: {err['confidence']:.0%}")
            print(f"   建議: 調整關鍵字或提示詞")
    
    print("\n" + "=" * 80)
    
    # 返回準確率
    return accuracy


def main():
    """主函數"""
    
    print("\n🤖 Multi-Agent 路由測試工具")
    
    # 檢查環境
    if not os.getenv('USE_MULTI_AGENT', 'true').lower() == 'true':
        print("⚠️  提示: USE_MULTI_AGENT 未啟用")
        print("請在 .env 中設定: USE_MULTI_AGENT=true")
        return
    
    # 執行測試
    try:
        accuracy = test_routing()
        
        if accuracy is None:
            print("\n❌ 測試無法執行")
            print("\n💡 可能的原因:")
            print("   1. Multi-Agent 系統未正確初始化")
            print("   2. 缺少 agents 模組或其依賴")
            print("   3. Python 路徑設定錯誤")
            print("\n🔧 解決方法:")
            print("   1. 確認 src/agents/ 目錄存在")
            print("   2. 檢查所有 Agent 檔案都已複製")
            print("   3. 執行: export PYTHONPATH=/path/to/kid_robot_project/src:$PYTHONPATH")
            return
        
        # 建議
        print("\n💡 改善建議:")
        if accuracy < 70:
            print("   準確率較低，建議:")
            print("   1. 使用更大的模型 (llama3.1:8b 或 qwen2.5:7b)")
            print("   2. 調整 gateway_agent.py 中的關鍵字列表")
            print("   3. 改進路由提示詞")
        elif accuracy < 90:
            print("   準確率良好，可以:")
            print("   1. 微調關鍵字匹配邏輯")
            print("   2. 增加更多測試案例")
        else:
            print("   ✅ 路由準確率優秀！系統運作正常")
        
    except Exception as e:
        print(f"\n❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()
    
    print()


if __name__ == "__main__":
    main()