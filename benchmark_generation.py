import json
import time
import statistics
from question_generator import QuestionGenerator
from typing import List, Dict


class QuestionBenchmark:
    """Benchmark question generation performance"""

    def __init__(self):
        self.gen = QuestionGenerator()
        self.results = {
            "mcq": [],
            "fillup": [],
            "coding": []
        }

    def benchmark_mcq(self, topic: str = "AWS VPC", difficulty: str = "hard",
                      iterations: int = 3, count: int = 3) -> Dict:
        """Benchmark MCQ generation multiple times"""

        print(f"\n{'=' * 70}")
        print(f"BENCHMARKING MCQ: {iterations} iterations × {count} questions")
        print(f"{'=' * 70}")

        times = []
        quality_scores = []

        for i in range(iterations):
            print(f"\n[Iteration {i + 1}/{iterations}]")
            try:
                questions, elapsed = self.gen.generate_mcq(topic, difficulty, count)
                times.append(elapsed)

                # Quality score: check if all fields are populated
                quality = self._score_mcq_quality(questions)
                quality_scores.append(quality)

                print(f"  ⏱️  Time: {elapsed:.2f}s for {len(questions)} questions")
                print(f"  📊 Quality: {quality:.1f}% (completeness)")
                print(f"  ✅ Valid questions: {len(questions)}/{count}")

                self.results["mcq"].extend(questions)

            except Exception as e:
                print(f"  ❌ Error: {e}")
                continue

        # Calculate statistics
        if times:
            avg_time = statistics.mean(times)
            avg_quality = statistics.mean(quality_scores)
            time_per_question = avg_time / count

            summary = {
                "type": "mcq",
                "iterations": iterations,
                "questions_per_iteration": count,
                "total_questions": len(self.results["mcq"]),
                "avg_time_seconds": round(avg_time, 2),
                "avg_time_per_question": round(time_per_question, 2),
                "min_time": round(min(times), 2),
                "max_time": round(max(times), 2),
                "avg_quality_percentage": round(avg_quality, 1)
            }

            self._print_benchmark_summary(summary)
            return summary

        return {}

    def benchmark_fillup(self, topic: str = "Data Transmission", difficulty: str = "hard",
                         iterations: int = 3, count: int = 3) -> Dict:
        """Benchmark Fill-up generation"""

        print(f"\n{'=' * 70}")
        print(f"BENCHMARKING FILL-UP: {iterations} iterations × {count} questions")
        print(f"{'=' * 70}")

        times = []
        quality_scores = []

        for i in range(iterations):
            print(f"\n[Iteration {i + 1}/{iterations}]")
            try:
                questions, elapsed = self.gen.generate_fillup(topic, difficulty, count)
                times.append(elapsed)

                quality = self._score_fillup_quality(questions)
                quality_scores.append(quality)

                print(f"  ⏱️  Time: {elapsed:.2f}s for {len(questions)} questions")
                print(f"  📊 Quality: {quality:.1f}% (completeness)")
                print(f"  ✅ Valid questions: {len(questions)}/{count}")

                self.results["fillup"].extend(questions)

            except Exception as e:
                print(f"  ❌ Error: {e}")
                continue

        if times:
            avg_time = statistics.mean(times)
            avg_quality = statistics.mean(quality_scores)
            time_per_question = avg_time / count

            summary = {
                "type": "fillup",
                "iterations": iterations,
                "questions_per_iteration": count,
                "total_questions": len(self.results["fillup"]),
                "avg_time_seconds": round(avg_time, 2),
                "avg_time_per_question": round(time_per_question, 2),
                "min_time": round(min(times), 2),
                "max_time": round(max(times), 2),
                "avg_quality_percentage": round(avg_quality, 1)
            }

            self._print_benchmark_summary(summary)
            return summary

        return {}

    def benchmark_coding(self, topic: str = "Spring Boot Services", difficulty: str = "hard",
                         iterations: int = 3, count: int = 2) -> Dict:
        """Benchmark Coding generation"""

        print(f"\n{'=' * 70}")
        print(f"BENCHMARKING CODING: {iterations} iterations × {count} questions")
        print(f"{'=' * 70}")

        times = []
        quality_scores = []

        for i in range(iterations):
            print(f"\n[Iteration {i + 1}/{iterations}]")
            try:
                questions, elapsed = self.gen.generate_coding(topic, difficulty, count)
                times.append(elapsed)

                quality = self._score_coding_quality(questions)
                quality_scores.append(quality)

                print(f"  ⏱️  Time: {elapsed:.2f}s for {len(questions)} questions")
                print(f"  📊 Quality: {quality:.1f}% (completeness)")
                print(f"  ✅ Valid questions: {len(questions)}/{count}")

                self.results["coding"].extend(questions)

            except Exception as e:
                print(f"  ❌ Error: {e}")
                continue

        if times:
            avg_time = statistics.mean(times)
            avg_quality = statistics.mean(quality_scores)
            time_per_question = avg_time / count

            summary = {
                "type": "coding",
                "iterations": iterations,
                "questions_per_iteration": count,
                "total_questions": len(self.results["coding"]),
                "avg_time_seconds": round(avg_time, 2),
                "avg_time_per_question": round(time_per_question, 2),
                "min_time": round(min(times), 2),
                "max_time": round(max(times), 2),
                "avg_quality_percentage": round(avg_quality, 1)
            }

            self._print_benchmark_summary(summary)
            return summary

        return {}

    def benchmark_all(self, mcq_iter=2, fillup_iter=2, coding_iter=2):
        """Run complete benchmark suite"""

        print("\n" + "🏃 STARTING COMPLETE BENCHMARK SUITE 🏃".center(70, "="))

        results = {
            "mcq": self.benchmark_mcq(iterations=mcq_iter, count=1),
            "fillup": self.benchmark_fillup(iterations=fillup_iter, count=1),
            "coding": self.benchmark_coding(iterations=coding_iter, count=2)
        }

        self._print_final_summary(results)

        return results

    def _score_mcq_quality(self, questions: List[Dict]) -> float:
        """Score MCQ quality (0-100)"""
        if not questions:
            return 0.0

        quality_count = 0
        for q in questions:
            # Check if all critical fields exist and are non-empty
            has_question = bool(q.get("question"))
            has_options = all(q.get("options", {}).values())
            has_answer = bool(q.get("correct_answer"))

            if has_question and has_options and has_answer:
                quality_count += 1

        return (quality_count / len(questions)) * 100

    def _score_fillup_quality(self, questions: List[Dict]) -> float:
        """Score Fill-up quality (0-100)"""
        if not questions:
            return 0.0

        quality_count = 0
        for q in questions:
            has_question = bool(q.get("question"))
            has_answer = bool(q.get("correct_word"))
            has_hint = bool(q.get("hint"))

            if has_question and has_answer and has_hint:
                quality_count += 1

        return (quality_count / len(questions)) * 100

    def _score_coding_quality(self, questions: List[Dict]) -> float:
        """Score Coding quality (0–100) based on schema completeness"""

        if not questions:
            return 0.0

        quality_count = 0

        for q in questions:
            has_question = bool(q.get("question"))
            has_input = bool(q.get("input"))
            has_output = bool(q.get("output"))
            has_constraints = bool(q.get("constraints"))
            has_example = bool(q.get("expected_output_example"))

            if (
                    has_question and
                    has_input and
                    has_output and
                    has_constraints and
                    has_example
            ):
                quality_count += 1

        return (quality_count / len(questions)) * 100

    def _print_benchmark_summary(self, summary: Dict):
        """Print formatted benchmark summary"""
        print("\n" + "-" * 70)
        print(f"SUMMARY: {summary['type'].upper()}")
        print("-" * 70)
        print(f"  Total Valid Questions: {summary['total_questions']}")
        print(f"  Average Time/Iteration: {summary['avg_time_seconds']}s")
        print(f"  Average Time/Question: {summary['avg_time_per_question']}s")
        print(f"  Time Range: {summary['min_time']}s - {summary['max_time']}s")
        print(f"  Quality Score: {summary['avg_quality_percentage']}%")
        print("-" * 70)

    def _print_final_summary(self, results: Dict):
        """Print final overall summary"""
        print("\n" + "=" * 70)
        print("FINAL BENCHMARK SUMMARY")
        print("=" * 70)

        total_questions = (results["mcq"].get("total_questions", 0) +
                           results["fillup"].get("total_questions", 0) +
                           results["coding"].get("total_questions", 0))

        print(f"\n📊 OVERALL STATISTICS:")
        print(f"  Total Questions Generated: {total_questions}")

        for qtype, result in results.items():
            if result:
                print(f"\n  {qtype.upper()}:")
                print(f"    ✅ Questions: {result['total_questions']}")
                print(f"    ⏱️  Avg Time: {result['avg_time_per_question']}s/question")
                print(f"    📈 Quality: {result['avg_quality_percentage']}%")

        print("\n" + "=" * 70)

    def save_results(self, filename: str = "benchmark_results.json"):
        """Save all generated questions to JSON for analysis"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to {filename}")


# Run benchmark
if __name__ == "__main__":
    benchmark = QuestionBenchmark()

    # Option 1: Benchmark each type separately
    print("\n🔍 INDIVIDUAL BENCHMARKS\n")
    benchmark.benchmark_mcq(iterations=2, count=1)
    benchmark.benchmark_fillup(iterations=2, count=1)
    # benchmark.benchmark_coding(iterations=2, count=2)

    # Option 2: Save all results
    benchmark.save_results("generated_questions.json")

    # Option 3: Run complete suite (uncomment to run)
    # results = benchmark.benchmark_all(mcq_iter=3, fillup_iter=3, coding_iter=2)
