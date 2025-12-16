import json
from question_generator import QuestionGenerator


def test_mcq_generation():
    """Test MCQ question generation"""
    print("\n" + "=" * 60)
    print("TEST 1: MCQ Question Generation")
    print("=" * 60)

    gen = QuestionGenerator()
    questions = gen.generate_mcq(
        topic="Python Basics",
        difficulty="easy",
        count=3
    )

    print(f"\nGenerated {len(questions)} questions")
    for q in questions:
        print(f"\n  Q{q['id']}: {q['question']}")
        print(f"  Options: {list(q['options'].values())}")
        print(f"  Answer: {q['correct_answer']}")

    assert len(questions) > 0, "No questions generated!"
    assert all(q['type'] == 'mcq' for q in questions)
    print("✅ TEST PASSED")


def test_fillup_generation():
    """Test fill-up question generation"""
    print("\n" + "=" * 60)
    print("TEST 2: Fill-up Question Generation")
    print("=" * 60)

    gen = QuestionGenerator()
    questions = gen.generate_fillup(
        topic="SQL",
        difficulty="medium",
        count=2
    )

    print(f"\nGenerated {len(questions)} questions")
    for q in questions:
        print(f"\n  Q{q['id']}: {q['question']}")
        print(f"  Answer: {q['correct_word']}")
        print(f"  Hint: {q['hint']}")

    assert len(questions) > 0, "No questions generated!"
    assert all(q['type'] == 'fillup' for q in questions)
    print("✅ TEST PASSED")


def test_coding_generation():
    """Test coding question generation"""
    print("\n" + "=" * 60)
    print("TEST 3: Coding Challenge Generation")
    print("=" * 60)

    gen = QuestionGenerator()
    questions = gen.generate_coding(
        topic="Python Algorithms",
        difficulty="medium",
        count=2
    )

    print(f"\nGenerated {len(questions)} questions")
    for q in questions:
        print(f"\n  Q{q['id']}: {q['question']}")
        print(f"  Function: {q['function_name']}")
        print(f"  Test Input: {q['test_input']}")
        print(f"  Expected: {q['expected_output']}")

    assert len(questions) > 0, "No questions generated!"
    assert all(q['type'] == 'coding' for q in questions)
    print("✅ TEST PASSED")


def test_json_validity():
    """Test that output is valid JSON"""
    print("\n" + "=" * 60)
    print("TEST 4: JSON Validity")
    print("=" * 60)

    gen = QuestionGenerator()
    questions = gen.generate_mcq(
        topic="Python",
        difficulty="easy",
        count=2
    )

    try:
        json_str = json.dumps(questions)
        parsed = json.loads(json_str)
        print(f"\n✅ Generated valid JSON ({len(json_str)} bytes)")
        print("✅ TEST PASSED")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        raise


def test_performance():
    """Benchmark question generation speed"""
    print("\n" + "=" * 60)
    print("TEST 5: Performance Benchmark")
    print("=" * 60)

    import time

    gen = QuestionGenerator()

    # Test MCQ
    start = time.time()
    mcq = gen.generate_mcq("Python", "easy", 5)
    mcq_time = time.time() - start
    print(f"\n5 MCQ questions: {mcq_time:.2f} seconds")
    print(f"Average per question: {mcq_time / 5:.2f} seconds")

    # Test Fill-up
    start = time.time()
    fillup = gen.generate_fillup("SQL", "medium", 5)
    fillup_time = time.time() - start
    print(f"\n5 Fill-up questions: {fillup_time:.2f} seconds")
    print(f"Average per question: {fillup_time / 5:.2f} seconds")

    # Test Coding
    start = time.time()
    coding = gen.generate_coding("Python", "easy", 3)
    coding_time = time.time() - start
    print(f"\n3 Coding questions: {coding_time:.2f} seconds")
    print(f"Average per question: {coding_time / 3:.2f} seconds")

    print("\n✅ TEST PASSED")


if __name__ == "__main__":
    try:
        test_mcq_generation()
        test_fillup_generation()
        test_coding_generation()
        test_json_validity()
        test_performance()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()