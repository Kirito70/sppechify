#!/usr/bin/env python3
"""
Database Seeding Script for Japanese Language Learning Application

This script seeds the database with initial Japanese sentence data for testing
and demonstration purposes. It creates a variety of sentences across different
JLPT levels and categories with auto-generated furigana.

Usage:
    python seed_database.py [--count 100] [--clear-first]

Author: Assistant
Date: 2025-01-20
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "backend-new" / "src"))

try:
    from app.core.db.database import async_get_db
    from app.models.japanese_sentence import JapaneseSentence
    from app.schemas.japanese_sentence import JapaneseSentenceCreateInternal
    from app.services.furigana_generator import FuriganaGenerator
    from app.services.japanese_processor import JapaneseProcessor
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import text
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this script from the project root directory")
    sys.exit(1)


# Sample Japanese sentences organized by JLPT level and category
SAMPLE_SENTENCES = {
    "N5": {
        "greetings": [
            ("こんにちは。", "Hello."),
            ("おはよう。", "Good morning."),
            ("ありがとうございます。", "Thank you very much."),
            ("すみません。", "Excuse me."),
            ("さようなら。", "Goodbye."),
        ],
        "basic_phrases": [
            ("私は学生です。", "I am a student."),
            ("これは本です。", "This is a book."),
            ("今日は暑いです。", "It's hot today."),
            ("家族は四人です。", "My family has four people."),
            ("日本語を勉強しています。", "I am studying Japanese."),
        ],
        "numbers_time": [
            ("今何時ですか。", "What time is it now?"),
            ("三時です。", "It's 3 o'clock."),
            ("私は二十歳です。", "I am 20 years old."),
            ("一月から三月まで。", "From January to March."),
            ("毎日六時に起きます。", "I wake up at 6 o'clock every day."),
        ]
    },
    "N4": {
        "daily_life": [
            ("昨日友達に会いました。", "I met a friend yesterday."),
            ("コンビニで買い物をします。", "I shop at the convenience store."),
            ("電車で会社に行きます。", "I go to the company by train."),
            ("週末は映画を見ました。", "I watched a movie on the weekend."),
            ("料理を作ることができます。", "I can cook."),
        ],
        "weather_seasons": [
            ("今日は雨が降っています。", "It's raining today."),
            ("春になって花が咲きました。", "Spring came and flowers bloomed."),
            ("夏休みに海に行きました。", "I went to the sea during summer vacation."),
            ("秋の紅葉がきれいです。", "The autumn leaves are beautiful."),
            ("冬は雪がよく降ります。", "It snows a lot in winter."),
        ],
        "activities": [
            ("図書館で本を借りました。", "I borrowed a book from the library."),
            ("友達と一緒に遊びました。", "I played together with friends."),
            ("新しい服を買いました。", "I bought new clothes."),
            ("レストランで食事をしました。", "I had a meal at the restaurant."),
            ("公園を散歩しました。", "I took a walk in the park."),
        ]
    },
    "N3": {
        "work_study": [
            ("会議で発表をしなければなりません。", "I have to give a presentation at the meeting."),
            ("レポートの締切は来週です。", "The report deadline is next week."),
            ("同僚と協力してプロジェクトを進めています。", "I'm working with colleagues to advance the project."),
            ("資格を取るために勉強しています。", "I'm studying to get a qualification."),
            ("経験を積んでスキルを向上させたい。", "I want to gain experience and improve my skills."),
        ],
        "opinions_thoughts": [
            ("この本は非常に興味深いと思います。", "I think this book is very interesting."),
            ("彼の意見には賛成できません。", "I can't agree with his opinion."),
            ("環境問題について考える必要があります。", "We need to think about environmental issues."),
            ("日本の文化は複雑で面白いです。", "Japanese culture is complex and interesting."),
            ("技術の発展は社会を変えています。", "Technological development is changing society."),
        ]
    },
    "N2": {
        "complex_topics": [
            ("政府は新しい政策を発表しました。", "The government announced a new policy."),
            ("経済状況が改善されることを期待しています。", "We hope the economic situation will improve."),
            ("この研究結果は非常に重要な意味を持っています。", "This research result has very important significance."),
            ("国際協力の重要性がますます高まっています。", "The importance of international cooperation is increasingly growing."),
            ("技術革新により生活が便利になりました。", "Life has become convenient due to technological innovation."),
        ],
        "abstract_concepts": [
            ("努力すれば必ず成功するとは限りません。", "Hard work doesn't necessarily guarantee success."),
            ("失敗から学ぶことの方が多いかもしれません。", "We might learn more from failures."),
            ("多様性を認めることが重要です。", "It's important to acknowledge diversity."),
            ("伝統と革新のバランスを保つのは難しい。", "It's difficult to maintain a balance between tradition and innovation."),
            ("相互理解を深めることが平和につながります。", "Deepening mutual understanding leads to peace."),
        ]
    },
    "N1": {
        "advanced_topics": [
            ("持続可能な発展のために環境保護が不可欠です。", "Environmental protection is indispensable for sustainable development."),
            ("グローバル化により文化の多様性が失われつつあります。", "Cultural diversity is being lost due to globalization."),
            ("人工知能の発展が労働市場に与える影響を懸念しています。", "I'm concerned about the impact of AI development on the labor market."),
            ("少子高齢化社会における社会保障制度の見直しが急務です。", "Reviewing the social security system in an aging society with a declining birthrate is urgent."),
            ("気候変動対策には国際的な連携が欠かせません。", "International cooperation is essential for climate change measures."),
        ],
        "formal_expression": [
            ("本日はお忙しい中、貴重なお時間をいただき、誠にありがとうございます。", "Thank you very much for taking your valuable time despite your busy schedule today."),
            ("この度は、皆様のご協力により、プロジェクトが成功裏に終了いたしました。", "Thanks to everyone's cooperation, the project has been successfully completed."),
            ("社会情勢の変化に対応するため、組織改革を断行する必要があります。", "We need to implement organizational reform to respond to changes in social conditions."),
            ("専門知識を活用して、より効率的な解決策を提案させていただきます。", "We will propose more efficient solutions by utilizing specialized knowledge."),
            ("長期的な視点に立って、戦略的な判断を下すことが重要です。", "It's important to make strategic decisions from a long-term perspective."),
        ]
    }
}


class DatabaseSeeder:
    """Database seeding utility for Japanese sentences"""
    
    def __init__(self):
        self.furigana_generator = None
        self.japanese_processor = None
        self.total_inserted = 0
        self.total_errors = 0
        
        # Initialize processors
        try:
            self.furigana_generator = FuriganaGenerator()
            self.japanese_processor = JapaneseProcessor()
            print("✓ Japanese processing services initialized")
        except Exception as e:
            print(f"⚠ Warning: Could not initialize Japanese processors: {e}")
            print("  Sentences will be inserted without furigana processing")
    
    async def clear_existing_sentences(self, db: AsyncSession) -> None:
        """Clear existing sentences from database"""
        try:
            # Delete all existing Japanese sentences
            await db.execute(text("DELETE FROM japanese_sentence"))
            await db.commit()
            print("✓ Cleared existing sentences from database")
        except Exception as e:
            await db.rollback()
            print(f"✗ Error clearing database: {e}")
            raise
    
    async def process_japanese_text(self, japanese_text: str) -> dict:
        """Process Japanese text to generate furigana and analysis"""
        result = {
            "hiragana_reading": None,
            "romaji_reading": None,
            "jlpt_level": None,
            "difficulty_level": 1
        }
        
        if not self.furigana_generator or not self.japanese_processor:
            return result
        
        try:
            # Generate furigana
            furigana_result = await self.furigana_generator.generate_furigana(japanese_text)
            if not furigana_result.get("error"):
                result["hiragana_reading"] = furigana_result.get("furigana")
            
            # Get analysis
            analysis_result = await self.japanese_processor.analyze_japanese_text(japanese_text)
            if not analysis_result.get("error"):
                result["romaji_reading"] = analysis_result.get("romanization")
                result["jlpt_level"] = analysis_result.get("estimated_jlpt_level")
                result["difficulty_level"] = analysis_result.get("difficulty_estimate", 1)
        
        except Exception as e:
            print(f"⚠ Warning: Processing failed for '{japanese_text}': {e}")
        
        return result
    
    async def insert_sentence_batch(
        self, 
        db: AsyncSession, 
        sentences: list, 
        jlpt_level: str, 
        category: str
    ) -> None:
        """Insert a batch of sentences for a specific JLPT level and category"""
        print(f"  Processing {jlpt_level} - {category} ({len(sentences)} sentences)")
        
        for japanese_text, english_text in sentences:
            try:
                # Check if sentence already exists
                existing = await db.execute(
                    text("SELECT id FROM japanese_sentence WHERE japanese_text = :text"),
                    {"text": japanese_text}
                )
                if existing.fetchone():
                    print(f"    ⚠ Skipping duplicate: {japanese_text}")
                    continue
                
                # Process Japanese text
                processed_data = await self.process_japanese_text(japanese_text)
                
                # Create sentence data
                sentence_data = {
                    "japanese_text": japanese_text,
                    "english_translation": english_text,
                    "jlpt_level": jlpt_level,
                    "category": category,
                    "source": "Seed Data",
                    "difficulty_level": processed_data["difficulty_level"],
                    "hiragana_reading": processed_data["hiragana_reading"],
                    "romaji_reading": processed_data["romaji_reading"],
                    "is_active": True,
                    "times_studied": 0
                }
                
                # Create database record
                sentence = JapaneseSentence(**sentence_data)
                db.add(sentence)
                
                self.total_inserted += 1
                print(f"    ✓ Added: {japanese_text}")
            
            except Exception as e:
                self.total_errors += 1
                print(f"    ✗ Error inserting '{japanese_text}': {e}")
                await db.rollback()
                continue
        
        # Commit batch
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            print(f"    ✗ Error committing batch: {e}")
            raise
    
    async def seed_database(
        self, 
        max_sentences_per_level: int = None, 
        clear_first: bool = False
    ) -> None:
        """Seed database with sample Japanese sentences"""
        print("🌱 Starting database seeding...")
        
        # Get database session
        async for db in async_get_db():
            try:
                # Clear existing data if requested
                if clear_first:
                    print("🗑️  Clearing existing data...")
                    await self.clear_existing_sentences(db)
                
                # Process each JLPT level
                for jlpt_level, categories in SAMPLE_SENTENCES.items():
                    print(f"\n📚 Processing {jlpt_level} level sentences...")
                    
                    level_count = 0
                    for category, sentences in categories.items():
                        # Apply limit if specified
                        if max_sentences_per_level:
                            remaining = max_sentences_per_level - level_count
                            if remaining <= 0:
                                break
                            sentences = sentences[:remaining]
                        
                        await self.insert_sentence_batch(db, sentences, jlpt_level, category)
                        level_count += len(sentences)
                
                # Final statistics
                print(f"\n✅ Database seeding completed!")
                print(f"   📊 Total sentences inserted: {self.total_inserted}")
                print(f"   ⚠️  Total errors: {self.total_errors}")
                
                # Query final counts
                result = await db.execute(text("SELECT COUNT(*) FROM japanese_sentence"))
                total_count = result.scalar()
                print(f"   📈 Total sentences in database: {total_count}")
                
                # Show distribution by JLPT level
                print(f"\n📊 Distribution by JLPT level:")
                for level in ["N5", "N4", "N3", "N2", "N1"]:
                    result = await db.execute(
                        text("SELECT COUNT(*) FROM japanese_sentence WHERE jlpt_level = :level"),
                        {"level": level}
                    )
                    count = result.scalar()
                    if count > 0:
                        print(f"   {level}: {count} sentences")
            
            except Exception as e:
                print(f"✗ Seeding failed: {e}")
                await db.rollback()
                raise
            
            finally:
                break  # Exit the async generator loop


def main():
    """Main function to run the seeding script"""
    parser = argparse.ArgumentParser(description="Seed database with Japanese sentences")
    parser.add_argument(
        "--count", 
        type=int, 
        help="Maximum sentences per JLPT level (default: no limit)"
    )
    parser.add_argument(
        "--clear-first", 
        action="store_true",
        help="Clear existing sentences before seeding"
    )
    
    args = parser.parse_args()
    
    # Create seeder and run
    seeder = DatabaseSeeder()
    
    try:
        asyncio.run(seeder.seed_database(
            max_sentences_per_level=args.count,
            clear_first=args.clear_first
        ))
    except KeyboardInterrupt:
        print("\n❌ Seeding interrupted by user")
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()