<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Calculator;
use App\Services\CalculationService;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class CalculateController extends Controller
{
    public function __construct(
        private CalculationService $calculationService
    ) {}

    public function calculate(Request $request, string $slug): JsonResponse
    {
        $calculator = Calculator::where('slug', $slug)
            ->where('is_active', true)
            ->first();

        if (!$calculator) {
            return response()->json([
                'success' => false,
                'message' => 'Calculator not found',
            ], 404);
        }

        // Validate required inputs
        $inputFields = $calculator->input_fields;
        $inputs = $request->only(array_column($inputFields, 'name'));
        
        foreach ($inputFields as $field) {
            if ($field['required'] && empty($inputs[$field['name']])) {
                return response()->json([
                    'success' => false,
                    'message' => "Field '{$field['label']}' is required",
                ], 422);
            }
        }

        // Perform calculation
        $result = $this->calculationService->calculate($calculator, $inputs);

        // Increment usage counter if calculation was successful
        if ($result['success']) {
            $calculator->incrementUsage();
        }

        return response()->json($result);
    }
}
