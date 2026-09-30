import React, { useState } from 'react';

// ==============================================================================
// TYPESCRIPT INTERFACES
// ==============================================================================

export type PatternType = 'productivity' | 'prioritization' | 'deadline_habit' | 'fatigue';

export interface BehaviorPattern {
  id: string;
  title: string;
  pattern_type: PatternType;
  confidence: number; // 0 - 100%
  evidence_count: number;
  evidence_summary: string;
  weight: number; // multiplier e.g. 1.35
  is_active: boolean;
}

export interface Decision {
  id: string;
  timestamp: string;
  question: string;
  recommended_scenario: string;
  chosen_scenario: string;
  user_reason?: string;
  is_disagreement: boolean;
  actual_outcome?: string;
  outcome_rating?: number; // 1 to 5 stars
  outcome_feedback?: string;
}

export interface TwinHealthMetrics {
  personalization_score: number; // %
  data_coverage: number; // %
  decision_history_count: number;
  feedback_received_count: number;
  prediction_accuracy: number; // %
}

export interface Grade {
  id: string;
  subject_id: string;
  subject_name: string;
  assessment_name: string;
  score: number;
  max_score: number;
  weight: number; // %
  grade_letter: string;
  notes?: string;
  date_recorded: string;
}

export interface SubjectPerformance {
  subject_id: string;
  subject_name: string;
  credits: number;
  color?: string;
  current_percentage: number;
  current_grade: string;
  grade_points: number;
  target_grade: string;
  assessment_count: number;
}

export interface GradesOverviewData {
  cgpa_10: number;
  cgpa_4: number;
  total_credits: number;
  subject_breakdown: SubjectPerformance[];
  grades: Grade[];
}

// ==============================================================================
// COMPONENT 1: DIGITAL TWIN CONTINUOUS LEARNING DASHBOARD
// ==============================================================================

export const TwinLearningDashboard: React.FC<{
  health: TwinHealthMetrics;
  patterns: BehaviorPattern[];
  decisions: Decision[];
  onCorrectPattern: (pattern: BehaviorPattern) => void;
  onDeletePattern: (id: string) => void;
  onResetTwin: () => void;
  onSubmitFeedback: (decisionId: string, rating: number, outcome: string, notes: string) => void;
}> = ({
  health,
  patterns,
  decisions,
  onCorrectPattern,
  onDeletePattern,
  onResetTwin,
  onSubmitFeedback
}) => {
  const [selectedDecisionForFeedback, setSelectedDecisionForFeedback] = useState<Decision | null>(null);
  const [feedbackRating, setFeedbackRating] = useState<number>(5);
  const [outcomeText, setOutcomeText] = useState<string>('');
  const [feedbackNote, setFeedbackNote] = useState<string>('');

  const getPatternTypeBadge = (type: PatternType) => {
    switch (type) {
      case 'productivity':
        return <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">Productivity</span>;
      case 'prioritization':
        return <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-cyan-100 text-cyan-800">Prioritization</span>;
      case 'deadline_habit':
        return <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800">Deadline Habit</span>;
      case 'fatigue':
        return <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-purple-100 text-purple-800">Fatigue & Stamina</span>;
    }
  };

  return (
    <div className="space-y-6 text-[#0E131F]">
      {/* 1. TWIN HEALTH METRICS CARDS */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <span className="text-xs text-slate-500 font-bold uppercase">Personalization</span>
          <div className="text-2xl font-black text-cyan-600">{health.personalization_score}%</div>
          <p className="text-[11px] text-slate-500">Based on decisions & sessions</p>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <span className="text-xs text-slate-500 font-bold uppercase">Data Coverage</span>
          <div className="text-2xl font-black text-indigo-600">{health.data_coverage}%</div>
          <p className="text-[11px] text-slate-500">Schedule & subjects populated</p>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <span className="text-xs text-slate-500 font-bold uppercase">Decision History</span>
          <div className="text-2xl font-black text-[#0E131F]">{health.decision_history_count}</div>
          <p className="text-[11px] text-slate-500">Dilemmas simulated</p>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <span className="text-xs text-slate-500 font-bold uppercase">Feedback Received</span>
          <div className="text-2xl font-black text-emerald-600">{health.feedback_received_count}</div>
          <p className="text-[11px] text-slate-500">Reality outcomes verified</p>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <span className="text-xs text-slate-500 font-bold uppercase">Prediction Accuracy</span>
          <div className="text-2xl font-black text-amber-600">{health.prediction_accuracy}%</div>
          <p className="text-[11px] text-slate-500">Real-world satisfaction score</p>
        </div>
      </div>

      {/* 2. ACTIVE LEARNED PATTERNS LIST */}
      <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-base font-extrabold text-[#0E131F]">Transparent Behavioral Patterns</h3>
            <p className="text-xs text-slate-500">The Twin continuously adjusts pattern weights based on your choices and overrides.</p>
          </div>
          <button
            onClick={onResetTwin}
            className="px-3.5 py-1.5 rounded-xl border border-rose-300 text-rose-700 hover:bg-rose-50 text-xs font-bold transition"
          >
            ↺ Reset Twin to Baseline
          </button>
        </div>

        <div className="space-y-3">
          {patterns.map((p) => (
            <div key={p.id} className="p-4 rounded-2xl border border-slate-200 bg-slate-50/50 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div className="space-y-1.5 max-w-xl">
                <div className="flex items-center gap-2">
                  {getPatternTypeBadge(p.pattern_type)}
                  <h4 className="font-extrabold text-sm text-[#0E131F]">{p.title}</h4>
                  <span className="text-xs font-mono font-bold text-slate-500 bg-slate-200 px-2 py-0.5 rounded">
                    ×{p.weight} weight
                  </span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">{p.evidence_summary}</p>
                <div className="text-[11px] text-slate-500 flex items-center gap-3">
                  <span>Confidence: <strong>{p.confidence}%</strong></span>
                  <span>•</span>
                  <span>Evidence: <strong>{p.evidence_count} events</strong></span>
                  <span>•</span>
                  <span className={p.is_active ? 'text-emerald-700 font-bold' : 'text-slate-400 font-bold'}>
                    {p.is_active ? '● Active in Simulations' : '○ Muted'}
                  </span>
                </div>
              </div>

              <div className="flex gap-2 text-xs font-bold">
                <button
                  onClick={() => onCorrectPattern(p)}
                  className="px-3 py-1.5 rounded-xl bg-white border border-slate-300 hover:border-cyan-500 shadow-sm transition"
                >
                  ✏️ Correct Pattern
                </button>
                <button
                  onClick={() => onDeletePattern(p.id)}
                  className="px-3 py-1.5 rounded-xl bg-white border border-slate-300 text-slate-500 hover:text-rose-600 shadow-sm transition"
                >
                  Archive
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 3. DECISION HISTORY & PREDICTION VS. REALITY */}
      <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="text-base font-extrabold text-[#0E131F]">Prediction vs. Reality Decision Log</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0E131F] text-white">
              <tr>
                <th className="p-3">Dilemma Question</th>
                <th className="p-3">Recommended</th>
                <th className="p-3">Chosen Scenario</th>
                <th className="p-3">Alignment</th>
                <th className="p-3">Real-World Outcome</th>
                <th className="p-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {decisions.map((d) => (
                <tr key={d.id} className="hover:bg-slate-50">
                  <td className="p-3 font-bold text-[#0E131F] max-w-xs">{d.question}</td>
                  <td className="p-3 text-slate-600">{d.recommended_scenario}</td>
                  <td className="p-3 font-semibold text-cyan-700">{d.chosen_scenario}</td>
                  <td className="p-3">
                    {d.is_disagreement ? (
                      <span className="px-2 py-0.5 rounded font-bold bg-amber-100 text-amber-800 text-[10px]">
                        Override (Disagreed)
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded font-bold bg-emerald-100 text-emerald-800 text-[10px]">
                        Twin Aligned
                      </span>
                    )}
                  </td>
                  <td className="p-3 text-slate-600">
                    {d.actual_outcome ? (
                      <div>
                        <div>{d.actual_outcome}</div>
                        <div className="text-amber-500 font-bold text-xs mt-0.5">
                          {'★'.repeat(d.outcome_rating || 5)}{'☆'.repeat(5 - (d.outcome_rating || 5))}
                        </div>
                      </div>
                    ) : (
                      <span className="text-slate-400 italic">Pending reality verification</span>
                    )}
                  </td>
                  <td className="p-3 text-right">
                    <button
                      onClick={() => {
                        setSelectedDecisionForFeedback(d);
                        setOutcomeText(d.actual_outcome || '');
                        setFeedbackRating(d.outcome_rating || 5);
                        setFeedbackNote(d.outcome_feedback || '');
                      }}
                      className="px-3 py-1 rounded-xl bg-cyan-50 text-cyan-800 font-bold hover:bg-cyan-100 transition"
                    >
                      ⭐ {d.outcome_rating ? 'Edit Rating' : 'Log Outcome'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* FEEDBACK MODAL */}
      {selectedDecisionForFeedback && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white p-6 rounded-3xl max-w-md w-full space-y-4 shadow-2xl">
            <h3 className="font-extrabold text-base text-[#0E131F]">Prediction vs. Reality Feedback</h3>
            <p className="text-xs text-slate-600">
              How did your choice: <strong>{selectedDecisionForFeedback.chosen_scenario}</strong> turn out in real life?
            </p>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block font-bold mb-1">Satisfaction Rating (1 to 5 Stars)</label>
                <div className="flex gap-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => setFeedbackRating(star)}
                      className={`text-xl ${feedbackRating >= star ? 'text-amber-400' : 'text-slate-300'}`}
                    >
                      ★
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block font-bold mb-1">What actually happened?</label>
                <textarea
                  rows={3}
                  value={outcomeText}
                  onChange={(e) => setOutcomeText(e.target.value)}
                  placeholder="e.g. Completed all lab modules before traveling; had zero anxiety."
                  className="w-full p-2.5 rounded-xl border border-slate-300 text-xs focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block font-bold mb-1">What should the Twin learn next time?</label>
                <input
                  type="text"
                  value={feedbackNote}
                  onChange={(e) => setFeedbackNote(e.target.value)}
                  placeholder="e.g. Pre-trip sprints work well for me."
                  className="w-full p-2.5 rounded-xl border border-slate-300 text-xs focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2 text-xs font-bold">
              <button
                onClick={() => setSelectedDecisionForFeedback(null)}
                className="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  onSubmitFeedback(selectedDecisionForFeedback.id, feedbackRating, outcomeText, feedbackNote);
                  setSelectedDecisionForFeedback(null);
                }}
                className="px-4 py-2 rounded-xl bg-cyan-500 text-[#0E131F] font-black shadow"
              >
                Save Reality Feedback
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// ==============================================================================
// COMPONENT 2: ACADEMIC GRADES & CGPA MANAGEMENT DASHBOARD
// ==============================================================================

export const GradesManagementDashboard: React.FC<{
  overview: GradesOverviewData;
  onRecordGrade: (grade: Omit<Grade, 'id' | 'grade_letter'>) => void;
  onDeleteGrade: (id: string) => void;
  onUpdateTarget: (subjectId: string, targetGrade: string) => void;
}> = ({ overview, onRecordGrade, onDeleteGrade, onUpdateTarget }) => {
  const [showAddModal, setShowAddModal] = useState<boolean>(false);
  const [search, setSearch] = useState<string>('');
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>('');
  const [assessmentName, setAssessmentName] = useState<string>('');
  const [score, setScore] = useState<string>('');
  const [maxScore, setMaxScore] = useState<string>('100');
  const [weight, setWeight] = useState<string>('20');
  const [notes, setNotes] = useState<string>('');

  const filteredGrades = overview.grades.filter(
    (g) =>
      g.assessment_name.toLowerCase().includes(search.toLowerCase()) ||
      g.subject_name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 text-[#0E131F]">
      {/* 1. CGPA HERO CARD */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-r from-[#0E131F] to-[#1e293b] text-white p-6 rounded-3xl shadow-lg space-y-2 col-span-2">
          <div className="flex justify-between items-center">
            <span className="text-xs uppercase font-extrabold text-cyan-400">Cumulative Academic Standing</span>
            <span className="text-xs bg-cyan-400/20 text-cyan-300 px-2.5 py-0.5 rounded-full font-bold">
              Verified Credits: {overview.total_credits}
            </span>
          </div>
          <div className="flex items-baseline gap-4">
            <div className="text-4xl sm:text-5xl font-black text-cyan-300">{overview.cgpa_10}</div>
            <div className="text-slate-400 text-sm font-semibold">/ 10.0 Scale</div>
            <div className="text-slate-400 text-sm font-semibold">•</div>
            <div className="text-xl font-bold text-white">{overview.cgpa_4} <span className="text-xs text-slate-400">/ 4.0 US Scale</span></div>
          </div>
          <p className="text-xs text-slate-300">
            Weighted across course credits. Consistent verified performance unlocks academic tiers.
          </p>
        </div>

        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <span className="text-xs font-bold text-slate-500 uppercase">Assessment Actions</span>
            <h4 className="text-base font-extrabold text-[#0E131F] mt-1">Track Examination</h4>
            <p className="text-xs text-slate-600 mt-1">Add assignments, quizzes, midterms or final exams.</p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="w-full mt-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-[#0E131F] font-black text-xs shadow-md transition"
          >
            + Record New Grade
          </button>
        </div>
      </div>

      {/* 2. SUBJECT PERFORMANCE BREAKDOWN CARDS */}
      <div className="space-y-3">
        <h3 className="text-base font-extrabold text-[#0E131F]">Subject Performance & Target Comparison</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {overview.subject_breakdown.map((s) => (
            <div key={s.subject_id} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-extrabold text-sm text-[#0E131F]">{s.subject_name}</h4>
                  <span className="text-[11px] text-slate-500 font-medium">{s.credits} Credits • {s.assessment_count} assessments</span>
                </div>
                <div className="text-right">
                  <span className="text-lg font-black text-cyan-600">{s.current_grade}</span>
                  <div className="text-[10px] text-slate-500">{s.current_percentage}%</div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="space-y-1">
                <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
                  <div
                    className="h-full bg-cyan-500 rounded-full"
                    style={{ width: `${Math.min(100, s.current_percentage)}%` }}
                  />
                </div>
                <div className="flex justify-between text-[10px] text-slate-500 font-bold">
                  <span>Current: {s.current_grade}</span>
                  <span>Target: {s.target_grade}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 3. ASSESSMENT HISTORY TABLE */}
      <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <h3 className="text-base font-extrabold text-[#0E131F]">Assessment Results History</h3>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search assessments..."
            className="px-3.5 py-2 rounded-xl border border-slate-200 text-xs w-full sm:w-64 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0E131F] text-white">
              <tr>
                <th className="p-3">Subject</th>
                <th className="p-3">Assessment</th>
                <th className="p-3">Score</th>
                <th className="p-3">Percentage</th>
                <th className="p-3">Grade</th>
                <th className="p-3">Weight</th>
                <th className="p-3">Date</th>
                <th className="p-3">Notes</th>
                <th className="p-3 text-right">Delete</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredGrades.map((g) => (
                <tr key={g.id} className="hover:bg-slate-50">
                  <td className="p-3 font-bold text-[#0E131F]">{g.subject_name}</td>
                  <td className="p-3 text-slate-700 font-semibold">{g.assessment_name}</td>
                  <td className="p-3 font-mono font-bold text-slate-800">{g.score} / {g.max_score}</td>
                  <td className="p-3 font-bold text-cyan-700">{Math.round((g.score / g.max_score) * 100)}%</td>
                  <td className="p-3 font-black text-[#0E131F]">{g.grade_letter}</td>
                  <td className="p-3 text-slate-500">{g.weight}%</td>
                  <td className="p-3 text-slate-500">{g.date_recorded}</td>
                  <td className="p-3 text-slate-600 max-w-xs truncate">{g.notes || '-'}</td>
                  <td className="p-3 text-right">
                    <button
                      onClick={() => onDeleteGrade(g.id)}
                      className="text-slate-400 hover:text-rose-600 font-bold"
                    >
                      ✕
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* 4. SCIENTIFIC NOTICE DISCLAIMER */}
        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 text-slate-500 text-[11px] leading-relaxed">
          <strong>Scientific Notice Disclaimer:</strong> Grades reflect historical performance and do not predict future outcomes with certainty.
        </div>
      </div>

      {/* RECORD GRADE MODAL */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white p-6 rounded-3xl max-w-md w-full space-y-4 shadow-2xl">
            <h3 className="font-extrabold text-base text-[#0E131F]">Record Assessment Result</h3>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block font-bold mb-1">Subject *</label>
                <select
                  value={selectedSubjectId}
                  onChange={(e) => setSelectedSubjectId(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-slate-300 text-xs focus:outline-none"
                >
                  <option value="">Select Enrolled Subject</option>
                  {overview.subject_breakdown.map((s) => (
                    <option key={s.subject_id} value={s.subject_id}>
                      {s.subject_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-bold mb-1">Assessment Name *</label>
                <input
                  type="text"
                  value={assessmentName}
                  onChange={(e) => setAssessmentName(e.target.value)}
                  placeholder="e.g. Midterm 1, Quiz 2, Project"
                  className="w-full p-2.5 rounded-xl border border-slate-300 text-xs focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="block font-bold mb-1">Score *</label>
                  <input
                    type="number"
                    value={score}
                    onChange={(e) => setScore(e.target.value)}
                    placeholder="45"
                    className="w-full p-2.5 rounded-xl border border-slate-300 text-xs"
                  />
                </div>
                <div>
                  <label className="block font-bold mb-1">Max Score *</label>
                  <input
                    type="number"
                    value={maxScore}
                    onChange={(e) => setMaxScore(e.target.value)}
                    placeholder="50"
                    className="w-full p-2.5 rounded-xl border border-slate-300 text-xs"
                  />
                </div>
                <div>
                  <label className="block font-bold mb-1">Weight (%)</label>
                  <input
                    type="number"
                    value={weight}
                    onChange={(e) => setWeight(e.target.value)}
                    placeholder="25"
                    className="w-full p-2.5 rounded-xl border border-slate-300 text-xs"
                  />
                </div>
              </div>

              <div>
                <label className="block font-bold mb-1">Teacher / Instructor Notes</label>
                <input
                  type="text"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="e.g. Strong conceptual grasp of algorithms."
                  className="w-full p-2.5 rounded-xl border border-slate-300 text-xs"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2 text-xs font-bold">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  const sub = overview.subject_breakdown.find((s) => s.subject_id === selectedSubjectId);
                  onRecordGrade({
                    subject_id: selectedSubjectId,
                    subject_name: sub ? sub.subject_name : 'Subject',
                    assessment_name: assessmentName,
                    score: parseFloat(score) || 0,
                    max_score: parseFloat(maxScore) || 100,
                    weight: parseFloat(weight) || 20,
                    notes,
                    date_recorded: new Date().toISOString().split('T')[0]
                  });
                  setShowAddModal(false);
                }}
                className="px-4 py-2 rounded-xl bg-cyan-500 text-[#0E131F] font-black shadow"
              >
                Save Grade
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
