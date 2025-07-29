<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Support\Str;

class ApiKey extends Model
{
    protected $fillable = [
        'user_id',
        'key',
        'name',
        'requests_count',
        'requests_limit_per_month',
        'last_used_at',
        'is_active',
    ];

    protected $casts = [
        'last_used_at' => 'datetime',
        'is_active' => 'boolean',
    ];

    protected $hidden = [
        'key',
    ];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public static function generateKey(): string
    {
        return 'calcnest_' . Str::random(40);
    }

    public function incrementRequests(): void
    {
        $this->increment('requests_count');
        $this->update(['last_used_at' => now()]);
    }

    public function hasExceededLimit(): bool
    {
        return $this->requests_count >= $this->requests_limit_per_month;
    }
}
