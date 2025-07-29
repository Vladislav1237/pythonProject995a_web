<?php

use App\Http\Controllers\Api\CategoryController;
use App\Http\Controllers\Api\CalculatorController;
use App\Http\Controllers\Api\CalculateController;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

// Public API routes
Route::prefix('v1')->group(function () {
    // Categories
    Route::get('categories', [CategoryController::class, 'index']);
    Route::get('categories/{slug}', [CategoryController::class, 'show']);
    
    // Calculators
    Route::get('calculators', [CalculatorController::class, 'index']);
    Route::get('calculators/popular', [CalculatorController::class, 'popular']);
    Route::get('calculators/{slug}', [CalculatorController::class, 'show']);
    
    // Calculations
    Route::post('calculate/{slug}', [CalculateController::class, 'calculate']);
});
