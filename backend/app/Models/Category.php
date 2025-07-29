<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Category extends Model
{
    protected $fillable = [
        'name',
        'slug',
        'description',
        'icon',
        'sort_order',
        'is_active',
    ];

    protected $casts = [
        'is_active' => 'boolean',
    ];

    public function calculators(): HasMany
    {
        return $this->hasMany(Calculator::class);
    }

    public function activeCalculators(): HasMany
    {
        return $this->hasMany(Calculator::class)->where('is_active', true);
    }
}
