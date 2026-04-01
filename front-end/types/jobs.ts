export type JobCategory = {
  key: string;
  label: string;
};

export type JobPosting = {
  id: number;
  title: string;
  company_name: string;
  location: string;
  job_role: string;
  employment_type: string;
  experience_label: string;
  is_junior_friendly: boolean;
  required_skills: string;
  posted_at: string;
  deadline_at: string | null;
  external_url: string;
  source: string;
  ui_company_mark: string | null;
  ui_deadline_label: string | null;
  ui_tags: string[];
  ui_main_tasks: string[];
  ui_categories: string[];
  ui_recommendation_score: number | null;
  ui_recommendation_reasons: string[];
};

export type JobDetail = {
  id: number;
  title: string;
  company_name: string;
  job_role: string;
  overview: string;
  main_tasks: string[];
  requirements: string[];
  preferred_points: string[];
  benefits: string[];
  required_skills: string[];
  external_url: string;
  recommendation_score: number | null;
  recommendation_reasons: string[];
};
