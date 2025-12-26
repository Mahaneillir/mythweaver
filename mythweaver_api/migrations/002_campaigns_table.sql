-- Mythweaver Campaigns Table Migration
-- This creates the campaigns table for managing player campaigns

-- Create mythweaver_campaigns table
CREATE TABLE IF NOT EXISTS public.mythweaver_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    name TEXT NOT NULL,
    template_id TEXT NOT NULL DEFAULT 'broken_kingdom',
    
    -- Settings  
    tone TEXT DEFAULT 'balanced',
    difficulty TEXT DEFAULT 'normal',
    content_limits JSONB DEFAULT '{}'::jsonb,
    
    -- State
    current_scene_number INTEGER DEFAULT 1 NOT NULL,
    chapter_number INTEGER DEFAULT 1 NOT NULL,
    total_advances INTEGER DEFAULT 0 NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Enable Row Level Security on campaigns
ALTER TABLE public.mythweaver_campaigns ENABLE ROW LEVEL SECURITY;

-- Create RLS policy: Users can only access their own campaigns
CREATE POLICY "Users can only access their own campaigns"
    ON public.mythweaver_campaigns
    FOR ALL
    USING (auth.uid() = user_id);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS campaigns_user_id_idx ON public.mythweaver_campaigns(user_id);
CREATE INDEX IF NOT EXISTS campaigns_created_at_idx ON public.mythweaver_campaigns(created_at DESC);
CREATE INDEX IF NOT EXISTS campaigns_template_id_idx ON public.mythweaver_campaigns(template_id);

-- Create trigger to automatically update updated_at timestamp
DROP TRIGGER IF EXISTS campaigns_updated_at ON public.mythweaver_campaigns;
CREATE TRIGGER campaigns_updated_at
    BEFORE UPDATE ON public.mythweaver_campaigns
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON public.mythweaver_campaigns TO authenticated;
GRANT SELECT ON public.mythweaver_campaigns TO anon;
