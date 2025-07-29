<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Calculator extends Model
{
    protected $fillable = [
        'category_id',
        'name',
        'slug',
        'description',
        'formula_description',
        'input_fields',
        'formula_config',
        'meta_title',
        'meta_description',
        'seo_keywords',
        'usage_count',
        'is_active',
    ];

    protected $casts = [
        'input_fields' => 'array',
        'formula_config' => 'array',
        'seo_keywords' => 'array',
        'is_active' => 'boolean',
    ];

    public function category(): BelongsTo
    {
        return $this->belongsTo(Category::class);
    }

    public function incrementUsage(): void
    {
        $this->increment('usage_count');
    }
}
