<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Calculator;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class CalculatorController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $query = Calculator::where('is_active', true)
            ->with('category');

        if ($request->has('category')) {
            $query->whereHas('category', function ($q) use ($request) {
                $q->where('slug', $request->category);
            });
        }

        if ($request->has('search')) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('name', 'ILIKE', "%{$search}%")
                  ->orWhere('description', 'ILIKE', "%{$search}%");
            });
        }

        $calculators = $query->orderBy('usage_count', 'desc')
            ->paginate($request->get('per_page', 15));

        return response()->json([
            'success' => true,
            'data' => $calculators,
        ]);
    }

    public function show(string $slug): JsonResponse
    {
        $calculator = Calculator::where('slug', $slug)
            ->where('is_active', true)
            ->with('category')
            ->first();

        if (!$calculator) {
            return response()->json([
                'success' => false,
                'message' => 'Calculator not found',
            ], 404);
        }

        return response()->json([
            'success' => true,
            'data' => $calculator,
        ]);
    }

    public function popular(): JsonResponse
    {
        $calculators = Calculator::where('is_active', true)
            ->with('category')
            ->orderBy('usage_count', 'desc')
            ->limit(10)
            ->get();

        return response()->json([
            'success' => true,
            'data' => $calculators,
        ]);
    }
}
