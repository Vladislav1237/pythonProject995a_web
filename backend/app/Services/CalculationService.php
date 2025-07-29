<?php

namespace App\Services;

use App\Models\Calculator;
use Exception;

class CalculationService
{
    public function calculate(Calculator $calculator, array $inputs): array
    {
        $config = $calculator->formula_config;
        $type = $config['type'];

        try {
            switch ($type) {
                case 'bmi':
                    $result = $this->calculateBMI($inputs, $config);
                    break;
                
                case 'quadratic':
                    $result = $this->calculateQuadratic($inputs, $config);
                    break;
                
                case 'simple_multiplication':
                    $result = $this->calculateSimpleMultiplication($inputs, $config);
                    break;
                
                case 'unit_conversion_length':
                    $result = $this->calculateLengthConversion($inputs, $config);
                    break;
                
                case 'percentage':
                    $result = $this->calculatePercentage($inputs, $config);
                    break;
                
                default:
                    throw new Exception("Unknown calculation type: {$type}");
            }

            return [
                'success' => true,
                'result' => $result,
                'formula' => $calculator->formula_description,
                'inputs' => $inputs,
            ];
        } catch (Exception $e) {
            return [
                'success' => false,
                'error' => $e->getMessage(),
                'formula' => $calculator->formula_description,
                'inputs' => $inputs,
            ];
        }
    }

    private function calculateBMI(array $inputs, array $config): array
    {
        $weight = (float) $inputs['weight'];
        $height = (float) $inputs['height'];
        
        if ($weight <= 0 || $height <= 0) {
            throw new Exception('Weight and height must be positive numbers');
        }

        $heightInMeters = $height / 100;
        $bmi = $weight / ($heightInMeters * $heightInMeters);
        
        $category = '';
        if ($bmi < 18.5) {
            $category = 'Underweight';
        } elseif ($bmi < 25) {
            $category = 'Normal weight';
        } elseif ($bmi < 30) {
            $category = 'Overweight';
        } else {
            $category = 'Obese';
        }

        return [
            'value' => round($bmi, $config['decimal_places']),
            'unit' => $config['result_unit'],
            'category' => $category,
            'interpretation' => $this->getBMIInterpretation($bmi),
        ];
    }

    private function calculateQuadratic(array $inputs, array $config): array
    {
        $a = (float) $inputs['a'];
        $b = (float) $inputs['b'];
        $c = (float) $inputs['c'];
        
        if ($a == 0) {
            throw new Exception('Coefficient "a" cannot be zero in a quadratic equation');
        }

        $discriminant = $b * $b - 4 * $a * $c;
        
        if ($discriminant < 0) {
            return [
                'discriminant' => $discriminant,
                'roots' => 'No real roots',
                'type' => 'imaginary',
            ];
        } elseif ($discriminant == 0) {
            $root = -$b / (2 * $a);
            return [
                'discriminant' => $discriminant,
                'roots' => [round($root, $config['decimal_places'])],
                'type' => 'single',
            ];
        } else {
            $root1 = (-$b + sqrt($discriminant)) / (2 * $a);
            $root2 = (-$b - sqrt($discriminant)) / (2 * $a);
            return [
                'discriminant' => $discriminant,
                'roots' => [
                    round($root1, $config['decimal_places']),
                    round($root2, $config['decimal_places'])
                ],
                'type' => 'two_real',
            ];
        }
    }

    private function calculateSimpleMultiplication(array $inputs, array $config): array
    {
        $result = 1;
        foreach ($inputs as $key => $value) {
            if (is_numeric($value)) {
                $result *= (float) $value;
            }
        }

        return [
            'value' => round($result, $config['decimal_places']),
            'unit' => $config['result_unit'],
        ];
    }

    private function calculateLengthConversion(array $inputs, array $config): array
    {
        $value = (float) $inputs['value'];
        $fromUnit = $inputs['from_unit'];
        $toUnit = $inputs['to_unit'];
        
        if (!isset($config['conversions'][$fromUnit]) || !isset($config['conversions'][$toUnit])) {
            throw new Exception('Invalid unit provided');
        }

        // Convert to meters first (base unit)
        $valueInMeters = $value / $config['conversions'][$fromUnit];
        
        // Convert from meters to target unit
        $result = $valueInMeters * $config['conversions'][$toUnit];

        return [
            'value' => round($result, $config['decimal_places']),
            'from_unit' => $fromUnit,
            'to_unit' => $toUnit,
            'original_value' => $value,
        ];
    }

    private function calculatePercentage(array $inputs, array $config): array
    {
        $part = (float) $inputs['part'];
        $whole = (float) $inputs['whole'];
        
        if ($whole == 0) {
            throw new Exception('Whole value cannot be zero');
        }

        $percentage = ($part / $whole) * 100;

        return [
            'value' => round($percentage, $config['decimal_places']),
            'unit' => $config['result_unit'],
            'part' => $part,
            'whole' => $whole,
        ];
    }

    private function getBMIInterpretation(float $bmi): string
    {
        if ($bmi < 18.5) {
            return 'You are underweight. Consider consulting with a healthcare provider about healthy weight gain strategies.';
        } elseif ($bmi < 25) {
            return 'You have a normal weight. Great job maintaining a healthy weight!';
        } elseif ($bmi < 30) {
            return 'You are overweight. Consider adopting a healthier diet and increasing physical activity.';
        } else {
            return 'You are obese. It is recommended to consult with a healthcare provider about weight management strategies.';
        }
    }
}
