<?php

namespace Database\Seeders;

use App\Models\Category;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class CategorySeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $categories = [
            [
                'name' => 'Mathematics',
                'slug' => 'mathematics',
                'description' => 'Mathematical calculators for equations, geometry, and more',
                'icon' => '📐',
                'sort_order' => 1,
            ],
            [
                'name' => 'Health & Medicine',
                'slug' => 'health-medicine',
                'description' => 'Health calculators including BMI, body fat, and medical formulas',
                'icon' => '🏥',
                'sort_order' => 2,
            ],
            [
                'name' => 'Construction',
                'slug' => 'construction',
                'description' => 'Construction calculators for concrete, materials, and measurements',
                'icon' => '🏗️',
                'sort_order' => 3,
            ],
            [
                'name' => 'Finance',
                'slug' => 'finance',
                'description' => 'Financial calculators for loans, investments, and percentages',
                'icon' => '💰',
                'sort_order' => 4,
            ],
            [
                'name' => 'Unit Conversion',
                'slug' => 'unit-conversion',
                'description' => 'Convert between different units of measurement',
                'icon' => '🔄',
                'sort_order' => 5,
            ],
        ];

        foreach ($categories as $category) {
            Category::create($category);
        }
    }
}
