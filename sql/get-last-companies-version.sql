SELECT id, name, organization_id, created_at, updated_at
  FROM (
    SELECT id,
           name,
           organization_id,
           created_at,
           updated_at,
           ROW_NUMBER() OVER(PARTITION BY id ORDER BY COALESCE(updated_at, created_at) DESC, ingested_at DESC) AS rank
      FROM public.companies_events)
 WHERE rank = 1;