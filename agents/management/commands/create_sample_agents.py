from django.core.management.base import BaseCommand
from agents.models import AgentCategory, Agent


class Command(BaseCommand):
    help = 'Create sample agents for testing the marketplace'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample agents...')

        # Create categories
        categories_data = [
            {
                'name': 'Content Creation',
                'slug': 'content-creation',
                'description': 'AI agents for creating various types of content',
                'icon': '✍️'
            },
            {
                'name': 'Business & Marketing',
                'slug': 'business-marketing',
                'description': 'AI agents for business and marketing tasks',
                'icon': '📈'
            },
            {
                'name': 'Data & Analytics',
                'slug': 'data-analytics',
                'description': 'AI agents for data analysis and insights',
                'icon': '📊'
            },
            {
                'name': 'HR & Recruitment',
                'slug': 'hr-recruitment',
                'description': 'AI agents for human resources and recruitment',
                'icon': '👥'
            }
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = AgentCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat_data['slug']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create sample agents
        agents_data = [
            {
                'name': 'Professional Job Posting Creator',
                'slug': 'job-posting-creator',
                'short_description': 'Create professional, attractive job postings that attract top talent',
                'description': 'This AI agent helps you craft compelling job postings that stand out in the competitive talent market. It analyzes your requirements and creates comprehensive job descriptions with proper formatting, compelling language, and industry best practices.',
                'category': categories['hr-recruitment'],
                'price': 25.00,
                'icon': '💼',
                'is_featured': True,
                'n8n_webhook_url': 'http://localhost:5678/webhook/job-posting-webhook',
                'form_schema': {
                    'fields': [
                        {
                            'name': 'position_title',
                            'label': 'Position Title',
                            'type': 'text',
                            'required': True,
                            'placeholder': 'e.g., Senior Full Stack Developer'
                        },
                        {
                            'name': 'company_name',
                            'label': 'Company Name',
                            'type': 'text',
                            'required': True,
                            'placeholder': 'e.g., Quantum Technologies Inc.'
                        },
                        {
                            'name': 'job_description',
                            'label': 'Job Description',
                            'type': 'textarea',
                            'required': True,
                            'placeholder': 'Describe the role, responsibilities, and requirements...'
                        },
                        {
                            'name': 'seniority_level',
                            'label': 'Seniority Level',
                            'type': 'select',
                            'required': True,
                            'options': ['Entry Level', 'Mid Level', 'Senior', 'Executive']
                        },
                        {
                            'name': 'contract_type',
                            'label': 'Contract Type',
                            'type': 'select',
                            'required': True,
                            'options': ['Full-time', 'Part-time', 'Contract', 'Internship', 'Freelance']
                        },
                        {
                            'name': 'location',
                            'label': 'Location',
                            'type': 'text',
                            'required': True,
                            'placeholder': 'e.g., Dubai, UAE (Remote)'
                        },
                        {
                            'name': 'language',
                            'label': 'Language',
                            'type': 'select',
                            'required': True,
                            'options': ['English', 'Arabic', 'Spanish', 'French', 'German']
                        }
                    ]
                }
            },
            {
                'name': 'Social Media Ad Creator',
                'slug': 'social-media-ad-creator',
                'short_description': 'Generate compelling social media advertisements for multiple platforms',
                'description': 'Transform your product or service into engaging social media advertisements. This agent creates platform-specific ad copy, suggests visuals, and optimizes for maximum engagement and conversions across Facebook, Instagram, LinkedIn, and Twitter.',
                'category': categories['business-marketing'],
                'price': 35.00,
                'icon': '📱',
                'is_featured': True,
                'n8n_webhook_url': 'http://localhost:5678/webhook/social-ads-webhook',
                'form_schema': {
                    'fields': [
                        {
                            'name': 'product_service',
                            'label': 'Product/Service Name',
                            'type': 'text',
                            'required': True,
                            'placeholder': 'e.g., Premium Fitness App'
                        },
                        {
                            'name': 'target_audience',
                            'label': 'Target Audience',
                            'type': 'text',
                            'required': True,
                            'placeholder': 'e.g., Fitness enthusiasts aged 25-40'
                        },
                        {
                            'name': 'key_benefits',
                            'label': 'Key Benefits/Features',
                            'type': 'textarea',
                            'required': True,
                            'placeholder': 'List the main benefits and features...'
                        },
                        {
                            'name': 'platform',
                            'label': 'Social Media Platform',
                            'type': 'select',
                            'required': True,
                            'options': ['Facebook', 'Instagram', 'LinkedIn', 'Twitter', 'TikTok', 'All Platforms']
                        },
                        {
                            'name': 'ad_objective',
                            'label': 'Campaign Objective',
                            'type': 'select',
                            'required': True,
                            'options': ['Brand Awareness', 'Lead Generation', 'Sales/Conversions', 'Traffic', 'Engagement']
                        }
                    ]
                }
            },
            {
                'name': 'Business Data Analyzer',
                'slug': 'business-data-analyzer',
                'short_description': 'Analyze business data and generate actionable insights with visualizations',
                'description': 'Upload your business data and get comprehensive analysis with actionable insights. This agent processes various data formats, identifies trends, creates visualizations, and provides strategic recommendations to improve your business performance.',
                'category': categories['data-analytics'],
                'price': 45.00,
                'icon': '📈',
                'is_featured': False,
                'n8n_webhook_url': 'http://localhost:5678/webhook/data-analyzer-webhook',
                'form_schema': {
                    'fields': [
                        {
                            'name': 'data_type',
                            'label': 'Data Type',
                            'type': 'select',
                            'required': True,
                            'options': ['Sales Data', 'Customer Data', 'Financial Data', 'Marketing Data', 'Operational Data']
                        },
                        {
                            'name': 'data_description',
                            'label': 'Data Description',
                            'type': 'textarea',
                            'required': True,
                            'placeholder': 'Describe your data and what insights you are looking for...'
                        },
                        {
                            'name': 'time_period',
                            'label': 'Time Period',
                            'type': 'select',
                            'required': True,
                            'options': ['Last Month', 'Last Quarter', 'Last 6 Months', 'Last Year', 'Custom Range']
                        },
                        {
                            'name': 'analysis_focus',
                            'label': 'Analysis Focus',
                            'type': 'select',
                            'required': True,
                            'options': ['Trends & Patterns', 'Performance Metrics', 'Comparative Analysis', 'Predictive Insights', 'All Areas']
                        }
                    ]
                }
            },
            {
                'name': 'Blog Content Generator',
                'slug': 'blog-content-generator',
                'short_description': 'Create SEO-optimized blog posts and articles on any topic',
                'description': 'Generate high-quality, SEO-optimized blog content that engages your audience and drives traffic. This agent researches topics, creates outlines, writes compelling content, and suggests relevant keywords and meta descriptions.',
                'category': categories['content-creation'],
                'price': 30.00,
                'icon': '📝',
                'is_featured': False,
                'n8n_webhook_url': 'http://localhost:5678/webhook/blog-generator-webhook',
                'form_schema': {
                    'fields': [
                        {
                            'name': 'topic',
                            'label': 'Blog Topic',
                            'type': 'text',
                            'required': True,
                            'placeholder': 'e.g., Future of Artificial Intelligence in Healthcare'
                        },
                        {
                            'name': 'target_keywords',
                            'label': 'Target Keywords',
                            'type': 'text',
                            'required': False,
                            'placeholder': 'e.g., AI healthcare, medical AI, healthcare technology'
                        },
                        {
                            'name': 'word_count',
                            'label': 'Target Word Count',
                            'type': 'select',
                            'required': True,
                            'options': ['500-800 words', '800-1200 words', '1200-1800 words', '1800+ words']
                        },
                        {
                            'name': 'tone',
                            'label': 'Writing Tone',
                            'type': 'select',
                            'required': True,
                            'options': ['Professional', 'Conversational', 'Academic', 'Casual', 'Technical']
                        },
                        {
                            'name': 'audience',
                            'label': 'Target Audience',
                            'type': 'text',
                            'required': True,
                            'placeholder': 'e.g., Healthcare professionals, Tech enthusiasts, General readers'
                        }
                    ]
                }
            },
            {
                'name': 'Email Marketing Campaign Creator',
                'slug': 'email-campaign-creator',
                'short_description': 'Design and write effective email marketing campaigns that convert',
                'description': 'Create compelling email marketing campaigns that drive engagement and conversions. This agent designs email sequences, writes persuasive copy, suggests subject lines, and optimizes for deliverability and click-through rates.',
                'category': categories['business-marketing'],
                'price': 40.00,
                'icon': '📧',
                'is_featured': False,
                'n8n_webhook_url': 'http://localhost:5678/webhook/email-campaign-webhook',
                'form_schema': {
                    'fields': [
                        {
                            'name': 'campaign_goal',
                            'label': 'Campaign Goal',
                            'type': 'select',
                            'required': True,
                            'options': ['Product Launch', 'Lead Nurturing', 'Customer Retention', 'Sales Promotion', 'Event Promotion']
                        },
                        {
                            'name': 'product_service',
                            'label': 'Product/Service',
                            'type': 'text',
                            'required': True,
                            'placeholder': 'What are you promoting?'
                        },
                        {
                            'name': 'target_audience',
                            'label': 'Target Audience',
                            'type': 'text', 
                            'required': True,
                            'placeholder': 'Describe your email subscribers/target audience'
                        },
                        {
                            'name': 'email_count',
                            'label': 'Number of Emails',
                            'type': 'select',
                            'required': True,
                            'options': ['Single Email', '3-Email Series', '5-Email Series', '7-Email Series']
                        },
                        {
                            'name': 'brand_voice',
                            'label': 'Brand Voice',
                            'type': 'select',
                            'required': True,
                            'options': ['Professional', 'Friendly', 'Authoritative', 'Playful', 'Luxury']
                        }
                    ]
                }
            },
            {
                'name': 'Resume & CV Optimizer',
                'slug': 'resume-cv-optimizer',
                'short_description': 'Optimize resumes and CVs for specific job applications and ATS systems',
                'description': 'Transform your resume into a powerful job-winning tool. This agent analyzes job descriptions, optimizes your resume for ATS systems, suggests improvements, and tailors content to match specific positions and industries.',
                'category': categories['hr-recruitment'],
                'price': 20.00,
                'icon': '📄',
                'is_featured': False,
                'n8n_webhook_url': 'http://localhost:5678/webhook/resume-optimizer-webhook',
                'form_schema': {
                    'fields': [
                        {
                            'name': 'current_resume',
                            'label': 'Current Resume Content',
                            'type': 'textarea',
                            'required': True,
                            'placeholder': 'Paste your current resume content here...'
                        },
                        {
                            'name': 'job_description',
                            'label': 'Target Job Description',
                            'type': 'textarea',
                            'required': True,
                            'placeholder': 'Paste the job description you are applying for...'
                        },
                        {
                            'name': 'industry',
                            'label': 'Industry',
                            'type': 'select',
                            'required': True,
                            'options': ['Technology', 'Finance', 'Healthcare', 'Marketing', 'Sales', 'Education', 'Engineering', 'Other']
                        },
                        {
                            'name': 'experience_level',
                            'label': 'Experience Level',
                            'type': 'select',
                            'required': True,
                            'options': ['Entry Level (0-2 years)', 'Mid Level (3-5 years)', 'Senior (6-10 years)', 'Executive (10+ years)']
                        }
                    ]
                }
            }
        ]

        # Create agents
        for agent_data in agents_data:
            agent, created = Agent.objects.get_or_create(
                slug=agent_data['slug'],
                defaults=agent_data
            )
            if created:
                self.stdout.write(f'Created agent: {agent.name}')
            else:
                # Update existing agent with new data
                for key, value in agent_data.items():
                    if key != 'slug':
                        setattr(agent, key, value)
                agent.save()
                self.stdout.write(f'Updated agent: {agent.name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created/updated {len(categories_data)} categories and {len(agents_data)} agents'
            )
        )