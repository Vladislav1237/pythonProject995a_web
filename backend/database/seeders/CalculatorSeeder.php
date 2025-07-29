<?php

namespace Database\Seeders;

use App\Models\Calculator;
use App\Models\Category;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class CalculatorSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $healthCategory = Category::where('slug', 'health-medicine')->first();
        $mathCategory = Category::where('slug', 'mathematics')->first();
        $constructionCategory = Category::where('slug', 'construction')->first();
        $financeCategory = Category::where('slug', 'finance')->first();
        $unitCategory = Category::where('slug', 'unit-conversion')->first();

        $calculators = [
            [
                'category_id' => $healthCategory->id,
                'name' => 'BMI Calculator',
                'slug' => 'bmi',
                'description' => 'Calculate your Body Mass Index (BMI) to determine if you are underweight, normal weight, overweight, or obese.',
                'formula_description' => 'BMI = weight (kg) / height (m)²',
                'input_fields' => [
                    [
                        'name' => 'weight',
                        'label' => 'Weight',
                        'type' => 'number',
                        'unit' => 'kg',
                        'min' => 1,
                        'max' => 1000,
                        'step' => 0.1,
                        'required' => true
                    ],
                    [
                        'name' => 'height',
                        'label' => 'Height',
                        'type' => 'number',
                        'unit' => 'cm',
                        'min' => 50,
                        'max' => 300,
                        'step' => 1,
                        'required' => true
                    ]
                ],
                'formula_config' => [
                    'type' => 'bmi',
                    'formula' => 'weight / ((height / 100) ** 2)',
                    'result_unit' => 'kg/m²',
                    'decimal_places' => 1
                ],
                'meta_title' => 'BMI Calculator - Calculate Your Body Mass Index',
                'meta_description' => 'Free BMI calculator to determine your Body Mass Index. Find out if you are underweight, normal, overweight or obese.',
                'seo_keywords' => ['bmi calculator', 'body mass index', 'weight calculator', 'health calculator']
            ],
            [
                'category_id' => $mathCategory->id,
                'name' => 'Quadratic Equation Solver',
                'slug' => 'quadratic-equation',
                'description' => 'Solve quadratic equations of the form ax² + bx + c = 0 using the quadratic formula.',
                'formula_description' => 'x = (-b ± √(b² - 4ac)) / (2a)',
                'input_fields' => [
                    [
                        'name' => 'a',
                        'label' => 'Coefficient a',
                        'type' => 'number',
                        'step' => 0.1,
                        'required' => true
                    ],
                    [
                        'name' => 'b',
                        'label' => 'Coefficient b',
                        'type' => 'number',
                        'step' => 0.1,
                        'required' => true
                    ],
                    [
                        'name' => 'c',
                        'label' => 'Coefficient c',
                        'type' => 'number',
                        'step' => 0.1,
                        'required' => true
                    ]
                ],
                'formula_config' => [
                    'type' => 'quadratic',
                    'formula' => 'quadratic_formula',
                    'decimal_places' => 3
                ],
                'meta_title' => 'Quadratic Equation Calculator - Solve ax² + bx + c = 0',
                'meta_description' => 'Free quadratic equation solver. Enter coefficients a, b, c to find the roots of any quadratic equation.',
                'seo_keywords' => ['quadratic equation', 'quadratic formula', 'math calculator', 'equation solver']
            ],
            [
                'category_id' => $constructionCategory->id,
                'name' => 'Concrete Volume Calculator',
                'slug' => 'concrete-volume',
                'description' => 'Calculate the volume of concrete needed for your construction project.',
                'formula_description' => 'Volume = Length × Width × Height',
                'input_fields' => [
                    [
                        'name' => 'length',
                        'label' => 'Length',
                        'type' => 'number',
                        'unit' => 'm',
                        'min' => 0.1,
                        'step' => 0.1,
                        'required' => true
                    ],
                    [
                        'name' => 'width',
                        'label' => 'Width',
                        'type' => 'number',
                        'unit' => 'm',
                        'min' => 0.1,
                        'step' => 0.1,
                        'required' => true
                    ],
                    [
                        'name' => 'height',
                        'label' => 'Height',
                        'type' => 'number',
                        'unit' => 'm',
                        'min' => 0.01,
                        'step' => 0.01,
                        'required' => true
                    ]
                ],
                'formula_config' => [
                    'type' => 'simple_multiplication',
                    'formula' => 'length * width * height',
                    'result_unit' => 'm³',
                    'decimal_places' => 2
                ],
                'meta_title' => 'Concrete Volume Calculator - Calculate Cubic Meters',
                'meta_description' => 'Calculate how much concrete you need. Enter length, width, and height to get volume in cubic meters.',
                'seo_keywords' => ['concrete calculator', 'concrete volume', 'construction calculator', 'cubic meters']
            ],
            [
                'category_id' => $unitCategory->id,
                'name' => 'Length Converter',
                'slug' => 'length-converter',
                'description' => 'Convert between different units of length: meters, feet, inches, centimeters, and more.',
                'formula_description' => 'Convert between meters, feet, inches, and centimeters',
                'input_fields' => [
                    [
                        'name' => 'value',
                        'label' => 'Value',
                        'type' => 'number',
                        'step' => 0.001,
                        'required' => true
                    ],
                    [
                        'name' => 'from_unit',
                        'label' => 'From Unit',
                        'type' => 'select',
                        'options' => [
                            ['value' => 'm', 'label' => 'Meters'],
                            ['value' => 'ft', 'label' => 'Feet'],
                            ['value' => 'in', 'label' => 'Inches'],
                            ['value' => 'cm', 'label' => 'Centimeters']
                        ],
                        'required' => true
                    ],
                    [
                        'name' => 'to_unit',
                        'label' => 'To Unit',
                        'type' => 'select',
                        'options' => [
                            ['value' => 'm', 'label' => 'Meters'],
                            ['value' => 'ft', 'label' => 'Feet'],
                            ['value' => 'in', 'label' => 'Inches'],
                            ['value' => 'cm', 'label' => 'Centimeters']
                        ],
                        'required' => true
                    ]
                ],
                'formula_config' => [
                    'type' => 'unit_conversion_length',
                    'conversions' => [
                        'm' => 1,
                        'ft' => 3.28084,
                        'in' => 39.3701,
                        'cm' => 100
                    ],
                    'decimal_places' => 4
                ],
                'meta_title' => 'Length Unit Converter - Meters, Feet, Inches, CM',
                'meta_description' => 'Convert between different length units. Free conversion between meters, feet, inches, and centimeters.',
                'seo_keywords' => ['length converter', 'unit converter', 'meters to feet', 'inches to cm']
            ],
            [
                'category_id' => $financeCategory->id,
                'name' => 'Percentage Calculator',
                'slug' => 'percentage',
                'description' => 'Calculate percentages, percentage increase/decrease, and find what percentage one number is of another.',
                'formula_description' => 'Percentage = (part / whole) × 100',
                'input_fields' => [
                    [
                        'name' => 'part',
                        'label' => 'Part Value',
                        'type' => 'number',
                        'step' => 0.01,
                        'required' => true
                    ],
                    [
                        'name' => 'whole',
                        'label' => 'Whole Value',
                        'type' => 'number',
                        'step' => 0.01,
                        'min' => 0.01,
                        'required' => true
                    ]
                ],
                'formula_config' => [
                    'type' => 'percentage',
                    'formula' => '(part / whole) * 100',
                    'result_unit' => '%',
                    'decimal_places' => 2
                ],
                'meta_title' => 'Percentage Calculator - Calculate Percentages',
                'meta_description' => 'Free percentage calculator. Calculate what percentage one number is of another, percentage increase/decrease.',
                'seo_keywords' => ['percentage calculator', 'percent calculator', 'percentage formula', 'math calculator']
            ]
        ];

        foreach ($calculators as $calculator) {
            Calculator::create($calculator);
        }
    }
}
